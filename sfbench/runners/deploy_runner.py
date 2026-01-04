from pathlib import Path
import shutil

from sfbench import Task
from sfbench.runners.base_runner import BenchmarkRunner
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.sfdx import run_sfdx, parse_json_output, OrgCreationError, TimeoutError as SFDXTimeoutError


class DeployRunner(BenchmarkRunner):
    def __init__(self, task: Task, workspace_dir: Path, scratch_org_alias=None):
        super().__init__(task, workspace_dir, scratch_org_alias)
        self.org_username: str = None
    
    def setup(self) -> None:
        self._clone_and_checkout()
        
        self._create_scratch_org()
    
    def _create_scratch_org(self) -> None:
        from sfbench.utils.sfdx import create_scratch_org
        from pathlib import Path
        
        try:
            # Use the template from data/templates, not from repo
            template_file = Path(__file__).parent.parent.parent / "data" / "templates" / "project-scratch-def.json"
            
            # Generate unique alias
            import time
            alias = f"sfbench-{self.task.instance_id}-{int(time.time())}"
            
            # Use the utility function which handles errors properly
            # Run from repo_dir to avoid sfdx-project.json conflicts
            org_result = create_scratch_org(
                alias=alias,
                duration_days=1,
                definition_file=template_file,
                cwd=self.repo_dir  # Run from repo directory to use its sfdx-project.json
            )
            
            self.org_username = org_result.get('username')
            
            if not self.org_username:
                raise OrgCreationError("Failed to get org username", 1, "No username in response")
                
        except OrgCreationError:
            raise
        except Exception as e:
            raise OrgCreationError(f"Scratch org creation failed: {str(e)}", 1, str(e))
    
    def evaluate(self) -> TestResult:
        try:
            exit_code, stdout, stderr = run_sfdx(
                self.task.validation.command,
                cwd=self.repo_dir,
                timeout=self.task.timeouts.run
            )
            
            result = parse_json_output(stdout)
            
            deploy_result = result.get('result', {})
            status_value = deploy_result.get('status', '').lower()
            
            if status_value == 'succeeded' or deploy_result.get('success', False):
                status = TestStatus.PASS
            else:
                status = TestStatus.FAIL
            
            return TestResult(
                task_id=self.task.instance_id,
                status=status,
                duration=self._get_duration(),
                details={
                    'deploy_status': status_value,
                    'components_deployed': deploy_result.get('numberComponentsDeployed', 0),
                    'components_total': deploy_result.get('numberComponentsTotal', 0)
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
