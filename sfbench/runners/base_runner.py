from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import time

from sfbench import Task
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.git import clone_repository, checkout_commit, apply_patch, PatchApplicationError
from sfbench.utils.sfdx import PlatformLimitationError
from sfbench.utils.retry import retry_with_backoff


class BenchmarkRunner(ABC):
    def __init__(self, task: Task, workspace_dir: Path, scratch_org_alias: Optional[str] = None):
        self.task = task
        self.workspace_dir = workspace_dir
        # Ensure workspace directory exists
        workspace_dir.mkdir(parents=True, exist_ok=True)
        self.repo_dir = workspace_dir / task.instance_id
        self.scratch_org_alias = scratch_org_alias
        self.start_time: Optional[float] = None
        self.setup_complete = False
    
    def run(self, patch_diff: Optional[str] = None) -> TestResult:
        """
        Run the benchmark task with proper cleanup handling.
        
        CRITICAL: Always calls teardown() in finally block to prevent resource leaks.
        This ensures scratch orgs are deleted even if the script crashes.
        """
        self.start_time = time.time()
        
        try:
            self.setup()
            self.setup_complete = True
            
            if patch_diff:
                try:
                    self.inject_patch(patch_diff)
                except PatchApplicationError as e:
                    # Patch application failure = model failure (FAIL), not tool error (ERROR)
                    # The model generated a patch but it was invalid/corrupt/incomplete
                    duration = time.time() - self.start_time
                    return TestResult(
                        task_id=self.task.instance_id,
                        status=TestStatus.FAIL,
                        duration=duration,
                        error_message=f"Patch application failed: {str(e)}"
                    )
            
            result = self.evaluate()
            
            return result
            
        except PlatformLimitationError as e:
            # Platform limitation = model failure (FAIL), not tool error (ERROR)
            # The model generated a solution but it can't be tested due to platform constraints
            # This is a model limitation (didn't account for platform constraints)
            duration = time.time() - self.start_time
            return TestResult(
                task_id=self.task.instance_id,
                status=TestStatus.FAIL,
                duration=duration,
                error_message=f"Platform limitation: {str(e)}"
            )
        except Exception as e:
            # Only use ERROR for actual tool bugs (unexpected exceptions, code errors, etc.)
            # Patch failures and platform limitations are already handled above as FAIL
            duration = time.time() - self.start_time
            return TestResult(
                task_id=self.task.instance_id,
                status=TestStatus.ERROR,
                duration=duration,
                error_message=str(e)
            )
        finally:
            # CRITICAL: Always cleanup, even on error or crash
            # This prevents zombie scratch orgs from consuming daily limits
            try:
                self.teardown()
            except Exception as e:
                # Log cleanup failures but don't fail the task
                print(f"⚠️  Warning: Teardown failed for {self.task.instance_id}: {str(e)}")
                # TODO: Could log to a cleanup_failed.log file for manual cleanup
    
    @abstractmethod
    def setup(self) -> None:
        pass
    
    def inject_patch(self, patch_diff: str) -> None:
        """Inject patch with comprehensive logging and error handling."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Applying patch for task {self.task.instance_id}")
        logger.info(f"Patch size: {len(patch_diff)} characters, {len(patch_diff.splitlines())} lines")
        
        # Log patch preview for monitoring (first 200 chars to avoid log spam)
        patch_preview = patch_diff[:200].replace('\n', '\\n')
        logger.debug(f"Patch preview: {patch_preview}...")
        
        # Validate patch has content before attempting application
        if not patch_diff or not patch_diff.strip():
            logger.error(f"Empty patch received for task {self.task.instance_id}")
            raise ValueError("Cannot apply empty patch")
        
        # Check for basic diff structure
        has_diff_markers = any(marker in patch_diff for marker in ['diff --git', '---', '+++', '@@'])
        if not has_diff_markers:
            logger.warning(f"Patch for {self.task.instance_id} may not contain valid diff markers")
        
        # Apply patch with retry logic for transient failures
        @retry_with_backoff(max_retries=3, initial_delay=1.0, retry_on=(Exception,))
        def _apply_patch_with_retry():
            try:
                apply_patch(self.repo_dir, patch_diff, timeout=60)
            except Exception as e:
                # Log patch details before re-raising for better debugging
                error_msg = str(e)
                if "corrupt" in error_msg.lower() or "malformed" in error_msg.lower():
                    logger.error(f"PATCH ERROR for {self.task.instance_id}: Malformed/corrupt patch detected")
                    logger.error(f"Error details: {error_msg[:300]}")
                    # Log cleaned patch preview to help diagnose
                    from sfbench.utils.git import _clean_patch
                    try:
                        cleaned = _clean_patch(patch_diff)
                        logger.debug(f"Cleaned patch preview (first 500 chars): {cleaned[:500]}")
                        logger.debug(f"Cleaned patch has {len(cleaned.splitlines())} lines")
                    except Exception as clean_error:
                        logger.debug(f"Could not clean patch for preview: {clean_error}")
                raise
        
        try:
            _apply_patch_with_retry()
            logger.info(f"✅ Patch applied successfully for {self.task.instance_id}")
        except Exception as e:
            # Categorize errors: Tool issues vs Model issues
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            if any(keyword in error_lower for keyword in ["corrupt", "malformed", "does not contain valid diff", "unexpected end of file", "incomplete", "empty patch"]):
                # Model issue: AI generated invalid patch
                logger.error(
                    f"❌ PATCH APPLICATION FAILED (Model Issue): {self.task.instance_id}\n"
                    f"   Root Cause: AI model generated a corrupt, incomplete, or malformed patch.\n"
                    f"   Error: {error_msg[:500]}\n"
                    f"   Patch Size: {len(patch_diff)} chars, {len(patch_diff.splitlines())} lines\n"
                    f"   All 4 patch application strategies were attempted.\n"
                    f"   Patch validation and cleaning were performed, but patch structure is fundamentally invalid.\n"
                    f"   This is NOT a tool issue - the benchmark correctly identified an invalid patch from the AI model."
                )
                logger.debug(f"Failed patch preview (first 1000 chars):\n{patch_diff[:1000]}")
            elif "timeout" in error_lower:
                # Could be either - log as potential tool issue
                logger.warning(
                    f"⚠️  PATCH APPLICATION TIMEOUT: {self.task.instance_id}\n"
                    f"   Error: {error_msg[:500]}\n"
                    f"   Patch Size: {len(patch_diff)} chars\n"
                    f"   This may indicate a very large patch or system resource constraints."
                )
            else:
                # Unknown error - log with context
                logger.error(
                    f"❌ PATCH APPLICATION FAILED: {self.task.instance_id}\n"
                    f"   Error: {error_msg[:500]}\n"
                    f"   Patch Size: {len(patch_diff)} chars, {len(patch_diff.splitlines())} lines\n"
                    f"   All patch application strategies were attempted."
                )
                logger.debug(f"Failed patch preview (first 500 chars): {patch_diff[:500]}")
            raise
    
    @abstractmethod
    def evaluate(self) -> TestResult:
        pass
    
    @abstractmethod
    def teardown(self) -> None:
        pass
    
    def _clone_and_checkout(self) -> None:
        clone_repository(
            self.task.repo_url,
            self.repo_dir,
            timeout=self.task.timeouts.setup
        )
        checkout_commit(self.repo_dir, self.task.base_commit)
    
    def _get_duration(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
