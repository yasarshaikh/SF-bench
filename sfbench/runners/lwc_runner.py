from pathlib import Path
import subprocess
import shutil

from sfbench import Task
from sfbench.runners.base_runner import BenchmarkRunner
from sfbench.utils.scoring import TestResult, TestStatus


class LWCRunner(BenchmarkRunner):
    def __init__(self, task: Task, workspace_dir: Path, scratch_org_alias=None):
        super().__init__(task, workspace_dir, scratch_org_alias)
    
    def setup(self) -> None:
        self._clone_and_checkout()
        
        self._install_dependencies()
    
    def _install_dependencies(self) -> None:
        try:
            result = subprocess.run(
                ['npm', 'install'],
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                timeout=self.task.timeouts.setup
            )
            
            if result.returncode != 0:
                raise Exception(f"npm install failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception(f"npm install timed out after {self.task.timeouts.setup} seconds")
        except Exception as e:
            raise Exception(f"Failed to install dependencies: {str(e)}")
    
    def evaluate(self) -> TestResult:
        try:
            result = subprocess.run(
                self.task.validation.command,
                shell=True,
                cwd=str(self.repo_dir),
                capture_output=True,
                text=True,
                timeout=self.task.timeouts.run
            )
            
            exit_code = result.returncode
            
            if exit_code == 0:
                status = TestStatus.PASS
            else:
                status = TestStatus.FAIL
            
            return TestResult(
                task_id=self.task.instance_id,
                status=status,
                duration=self._get_duration(),
                details={
                    'exit_code': exit_code,
                    'stdout': result.stdout[-500:] if result.stdout else '',
                    'stderr': result.stderr[-500:] if result.stderr else ''
                }
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                task_id=self.task.instance_id,
                status=TestStatus.TIMEOUT,
                duration=self._get_duration(),
                error_message=f"Test execution timed out after {self.task.timeouts.run} seconds"
            )
        except Exception as e:
            return TestResult(
                task_id=self.task.instance_id,
                status=TestStatus.ERROR,
                duration=self._get_duration(),
                error_message=str(e)
            )
    
    def teardown(self) -> None:
        if self.repo_dir.exists():
            try:
                shutil.rmtree(self.repo_dir)
            except Exception as e:
                print(f"Warning: Failed to cleanup repo directory {self.repo_dir}: {str(e)}")
