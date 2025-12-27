from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import time

from sfbench import Task
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.git import clone_repository, checkout_commit, apply_patch


class BenchmarkRunner(ABC):
    def __init__(self, task: Task, workspace_dir: Path):
        self.task = task
        self.workspace_dir = workspace_dir
        self.repo_dir = workspace_dir / task.instance_id
        self.start_time: Optional[float] = None
        self.setup_complete = False
    
    def run(self, patch_diff: Optional[str] = None) -> TestResult:
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
            try:
                self.teardown()
            except Exception as e:
                print(f"Warning: Teardown failed for {self.task.instance_id}: {str(e)}")
    
    @abstractmethod
    def setup(self) -> None:
        pass
    
    def inject_patch(self, patch_diff: str) -> None:
        apply_patch(self.repo_dir, patch_diff, timeout=60)
    
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
