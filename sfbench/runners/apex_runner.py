from pathlib import Path
import json
import shutil

from sfbench import Task
from sfbench.runners.base_runner import BenchmarkRunner
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.sfdx import run_sfdx, parse_json_output, OrgCreationError, TimeoutError as SFDXTimeoutError


class ApexRunner(BenchmarkRunner):
    def __init__(self, task: Task, workspace_dir: Path):
        super().__init__(task, workspace_dir)
        self.org_username: str = None
    
    def setup(self) -> None:
        self._clone_and_checkout()
        
        self._create_scratch_org()
        
        self._push_metadata()
    
    def _create_scratch_org(self) -> None:
        try:
            exit_code, stdout, stderr = run_sfdx(
                "sf org create scratch --definition-file config/project-scratch-def.json --set-default --duration-days 1",
                cwd=self.repo_dir,
                timeout=self.task.timeouts.setup
            )
            
            result = parse_json_output(stdout)
            self.org_username = result.get('result', {}).get('username')
            
            if not self.org_username:
                raise OrgCreationError("Failed to get org username", 1, "No username in response")
                
        except OrgCreationError:
            raise
        except Exception as e:
            raise OrgCreationError(f"Scratch org creation failed: {str(e)}", 1, str(e))
    
    def _push_metadata(self) -> None:
        try:
            run_sfdx(
                "sf project deploy start",
                cwd=self.repo_dir,
                timeout=self.task.timeouts.setup
            )
        except Exception as e:
            raise Exception(f"Failed to push metadata: {str(e)}")
    
    def evaluate(self) -> TestResult:
        try:
            self._push_metadata()
            
            exit_code, stdout, stderr = run_sfdx(
                self.task.validation.command,
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
