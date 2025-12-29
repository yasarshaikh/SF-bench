from pathlib import Path
from typing import Optional
import json
import shutil

from sfbench import Task
from sfbench.runners.base_runner import BenchmarkRunner
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.sfdx import run_sfdx, parse_json_output, OrgCreationError, TimeoutError as SFDXTimeoutError


class ApexRunner(BenchmarkRunner):
    def __init__(self, task: Task, workspace_dir: Path, scratch_org_alias: Optional[str] = None):
        super().__init__(task, workspace_dir, scratch_org_alias)
        self.org_username: str = None
    
    def setup(self) -> None:
        self._clone_and_checkout()
        
        # Use shared scratch org if provided, otherwise create one
        if self.scratch_org_alias:
            self._use_shared_org()
        else:
            self._create_scratch_org()
        
        self._push_metadata()
    
    def _use_shared_org(self) -> None:
        """Use the shared scratch org created by the evaluation pipeline."""
        try:
            # Try to use alias directly first (CLI supports this)
            # Set the org as default (use alias - CLI supports it)
            run_sfdx(
                f"sf config set target-org {self.scratch_org_alias}",
                timeout=30
            )
            # Store alias as username fallback
            self.org_username = self.scratch_org_alias
            # Try to get username from alias (fallback)
            from sfbench.utils.sfdx import get_scratch_org_username
            self.org_username = get_scratch_org_username(self.scratch_org_alias)
            # If lookup fails, use alias directly (CLI should handle it)
            if not self.org_username:
                self.org_username = self.scratch_org_alias
                print(f"⚠️  Using alias directly: {self.scratch_org_alias}")
        except Exception as e:
            raise OrgCreationError(f"Failed to use shared org: {str(e)}", 1, str(e))
    
    def _create_scratch_org(self) -> None:
        """Create a new scratch org (fallback if no shared org provided)."""
        from sfbench.utils.sfdx import create_scratch_org
        from pathlib import Path
        
        try:
            # Use the template from data/templates, not from repo
            template_file = Path(__file__).parent.parent.parent / "data" / "templates" / "project-scratch-def.json"
            
            # Generate unique alias
            import time
            alias = f"sfbench-{self.task.instance_id}-{int(time.time())}"
            
            # Use the utility function which handles errors properly
            org_result = create_scratch_org(
                alias=alias,
                duration_days=1,
                definition_file=template_file
            )
            
            self.org_username = org_result.get('username')
            
            if not self.org_username:
                raise OrgCreationError("Failed to get org username", 1, "No username in response")
                
        except OrgCreationError:
            raise
        except Exception as e:
            raise OrgCreationError(f"Scratch org creation failed: {str(e)}", 1, str(e))
    
    def _push_metadata(self) -> None:
        try:
            cmd = "sf project deploy start"
            # Use username if available, otherwise use alias
            org_target = self.org_username or self.scratch_org_alias
            if org_target:
                cmd += f" --target-org {org_target}"
            run_sfdx(
                cmd,
                cwd=self.repo_dir,
                timeout=self.task.timeouts.setup
            )
        except Exception as e:
            raise Exception(f"Failed to push metadata: {str(e)}")
    
    def evaluate(self) -> TestResult:
        try:
            self._push_metadata()
            
            cmd = self.task.validation.command
            if self.scratch_org_alias and "--target-org" not in cmd:
                # Use username if available, otherwise use alias
                org_target = self.org_username or self.scratch_org_alias
                cmd += f" --target-org {org_target}"
            
            exit_code, stdout, stderr = run_sfdx(
                cmd,
                cwd=self.repo_dir,
                timeout=self.task.timeouts.run
            )
            
            result = parse_json_output(stdout)
            
            test_results = result.get('result', {})
            summary = test_results.get('summary', {})
            
            outcome = summary.get('outcome', '').lower()
            failures = summary.get('failing', 0)
            
            if outcome == 'passed' or failures == 0:
                status = TestStatus.PASS
            else:
                status = TestStatus.FAIL
            
            return TestResult(
                task_id=self.task.instance_id,
                status=status,
                duration=self._get_duration(),
                details={
                    'tests_run': summary.get('testsRan', 0),
                    'passed': summary.get('passing', 0),
                    'failed': failures,
                    'outcome': outcome
                }
            )
            
        except SFDXTimeoutError as e:
            return TestResult(
                task_id=self.task.instance_id,
                status=TestStatus.TIMEOUT,
                duration=self._get_duration(),
                error_message=str(e)
            )
        except Exception as e:
            return TestResult(
                task_id=self.task.instance_id,
                status=TestStatus.ERROR,
                duration=self._get_duration(),
                error_message=str(e)
            )
    
    def teardown(self) -> None:
        if self.org_username:
            try:
                run_sfdx(
                    f"sf org delete scratch --target-org {self.org_username} --no-prompt",
                    timeout=60,
                    json_output=False
                )
            except Exception as e:
                print(f"Warning: Failed to delete scratch org {self.org_username}: {str(e)}")
        
        if self.repo_dir.exists():
            try:
                shutil.rmtree(self.repo_dir)
            except Exception as e:
                print(f"Warning: Failed to cleanup repo directory {self.repo_dir}: {str(e)}")
