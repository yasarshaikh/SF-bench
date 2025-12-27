import json
from pathlib import Path
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from sfbench import Task, TaskType
from sfbench.runners.base_runner import BenchmarkRunner
from sfbench.runners.apex_runner import ApexRunner
from sfbench.runners.lwc_runner import LWCRunner
from sfbench.runners.deploy_runner import DeployRunner
from sfbench.runners.flow_runner import FlowRunner
from sfbench.runners.lightning_page_runner import LightningPageRunner
from sfbench.runners.community_runner import CommunityRunner
from sfbench.runners.architecture_runner import ArchitectureRunner
from sfbench.utils.scoring import TestResult, TestStatus, calculate_pass_rate
from sfbench.utils.validation import TaskValidator


class RunnerFactory:
    @staticmethod
    def create_runner(task: Task, workspace_dir: Path) -> BenchmarkRunner:
        if task.task_type == TaskType.APEX:
            return ApexRunner(task, workspace_dir)
        elif task.task_type == TaskType.LWC:
            return LWCRunner(task, workspace_dir)
        elif task.task_type == TaskType.DEPLOY:
            return DeployRunner(task, workspace_dir)
        elif task.task_type == TaskType.FLOW:
            return FlowRunner(task, workspace_dir)
        elif task.task_type == TaskType.LIGHTNING_PAGE:
            return LightningPageRunner(task, workspace_dir)
        elif task.task_type == TaskType.COMMUNITY:
            return CommunityRunner(task, workspace_dir)
        elif task.task_type == TaskType.ARCHITECTURE:
            return ArchitectureRunner(task, workspace_dir)
        elif task.task_type in (TaskType.PAGE_LAYOUT, TaskType.PROFILE, TaskType.PERMISSION_SET):
            # Use DeployRunner for metadata-based tasks
            return DeployRunner(task, workspace_dir)
        elif task.task_type in (TaskType.SALES_CLOUD, TaskType.SERVICE_CLOUD, TaskType.MARKETING_CLOUD,
                                TaskType.COMMERCE_CLOUD, TaskType.PLATFORM_CLOUD, TaskType.INTEGRATION,
                                TaskType.DATA_MODEL, TaskType.SECURITY):
            # Use ArchitectureRunner for cloud-specific and complex tasks
            return ArchitectureRunner(task, workspace_dir)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")


class BenchmarkEngine:
    def __init__(
        self,
        tasks_file: Path,
        workspace_dir: Path,
        results_dir: Path,
        max_workers: int = 3
    ):
        self.tasks_file = tasks_file
        self.workspace_dir = workspace_dir
        self.results_dir = results_dir
        self.max_workers = max_workers
        self.tasks: List[Task] = []
        self.results: List[TestResult] = []
        self._lock = threading.Lock()
    
    def load_tasks(self, validate: bool = True) -> None:
        """
        Load tasks from the tasks file.
        
        Args:
            validate: If True, validate task schemas before loading
        """
        if validate:
            try:
                self.tasks = TaskValidator.validate_and_load(self.tasks_file)
            except Exception as e:
                print(f"Task validation failed: {str(e)}")
                raise
        else:
            # Legacy loading without validation
            with open(self.tasks_file, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                self.tasks = [Task.from_dict(task_data) for task_data in data]
            else:
                self.tasks = [Task.from_dict(data)]
    
    def run_single_task(
        self,
        task: Task,
        patch_diff: Optional[str] = None
    ) -> TestResult:
        try:
            runner = RunnerFactory.create_runner(task, self.workspace_dir)
            result = runner.run(patch_diff)
            
            with self._lock:
                self.results.append(result)
                self._save_result(result)
            
            return result
            
        except Exception as e:
            print(f"Error running task {task.instance_id}: {str(e)}")
            result = TestResult(
                task_id=task.instance_id,
                status=TestStatus.ERROR,
                duration=0.0,
                error_message=str(e)
            )
            
            with self._lock:
                self.results.append(result)
                self._save_result(result)
            
            return result
    
    def run_all_tasks(self, patch_diffs: Optional[Dict[str, str]] = None) -> List[TestResult]:
        self.results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for task in self.tasks:
                patch = patch_diffs.get(task.instance_id) if patch_diffs else None
                future = executor.submit(self.run_single_task, task, patch)
                futures[future] = task.instance_id
            
            for future in as_completed(futures):
                task_id = futures[future]
                try:
                    result = future.result()
                    print(f"Completed: {task_id} - {result.status.value}")
                except Exception as e:
                    print(f"Failed: {task_id} - {str(e)}")
        
        self._save_summary()
        
        return self.results
    
    def _save_result(self, result: TestResult) -> None:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        result_file = self.results_dir / f"{result.task_id}.json"
        with open(result_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
    
    def _save_summary(self) -> None:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        summary = {
            'statistics': calculate_pass_rate(self.results),
            'results': [r.to_dict() for r in self.results]
        }
        
        summary_file = self.results_dir / 'summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nSummary saved to: {summary_file}")
        print(f"Pass Rate: {summary['statistics']['pass_rate']}%")
        print(f"Total: {summary['statistics']['total']}")
        print(f"Passed: {summary['statistics']['passed']}")
        print(f"Failed: {summary['statistics']['failed']}")
        print(f"Timeout: {summary['statistics']['timeout']}")
        print(f"Error: {summary['statistics']['error']}")
