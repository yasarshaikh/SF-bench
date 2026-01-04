from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import time

from sfbench import Task
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.git import clone_repository, checkout_commit, apply_patch


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
                self.inject_patch(patch_diff)
            
            result = self.evaluate()
            
            return result
            
        except Exception as e:
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
        logger.debug(f"Patch preview: {patch_diff[:500]}...")
        
        try:
            apply_patch(self.repo_dir, patch_diff, timeout=60)
            logger.info(f"Patch applied successfully for {self.task.instance_id}")
        except Exception as e:
            logger.error(f"Patch application failed for {self.task.instance_id}: {str(e)}")
            logger.debug(f"Failed patch content: {patch_diff[:1000]}")
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
