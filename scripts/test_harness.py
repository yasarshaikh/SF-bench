import unittest
from pathlib import Path
import json
import tempfile
import shutil

from sfbench import Task, TaskType
from sfbench.engine import RunnerFactory, BenchmarkEngine
from sfbench.utils.scoring import TestResult, TestStatus, calculate_pass_rate


class TestTaskDataclass(unittest.TestCase):
    def test_task_from_dict(self):
        data = {
            "instance_id": "test-001",
            "task_type": "APEX",
            "repo_url": "https://github.com/test/repo",
            "base_commit": "main",
            "problem_description": "Test problem",
            "validation": {
                "command": "sf apex run test",
                "expected_outcome": "Passed"
            },
            "timeouts": {
                "setup": 600,
                "run": 300
            }
        }
        
        task = Task.from_dict(data)
        
        self.assertEqual(task.instance_id, "test-001")
        self.assertEqual(task.task_type, TaskType.APEX)
        self.assertEqual(task.repo_url, "https://github.com/test/repo")
        self.assertEqual(task.validation.command, "sf apex run test")
        self.assertEqual(task.timeouts.setup, 600)
    
    def test_task_to_dict(self):
        data = {
            "instance_id": "test-001",
            "task_type": "LWC",
            "repo_url": "https://github.com/test/repo",
            "base_commit": "main",
            "problem_description": "Test problem",
            "validation": {
                "command": "npm test",
                "expected_outcome": "0"
            },
            "timeouts": {
                "setup": 300,
                "run": 180
            }
        }
        
        task = Task.from_dict(data)
        result = task.to_dict()
        
        self.assertEqual(result["instance_id"], "test-001")
        self.assertEqual(result["task_type"], "LWC")


class TestRunnerFactory(unittest.TestCase):
    def test_create_apex_runner(self):
        task = Task(
            instance_id="test-apex",
            task_type=TaskType.APEX,
            repo_url="https://github.com/test/repo",
            base_commit="main",
            problem_description="Test",
            validation={"command": "test", "expected_outcome": "pass"},
            timeouts={"setup": 600, "run": 300}
        )
        
        from sfbench.runners.apex_runner import ApexRunner
        runner = RunnerFactory.create_runner(task, Path("workspace"))
        self.assertIsInstance(runner, ApexRunner)
    
    def test_create_lwc_runner(self):
        task = Task(
            instance_id="test-lwc",
            task_type=TaskType.LWC,
            repo_url="https://github.com/test/repo",
            base_commit="main",
            problem_description="Test",
            validation={"command": "test", "expected_outcome": "0"},
            timeouts={"setup": 300, "run": 180}
        )
        
        from sfbench.runners.lwc_runner import LWCRunner
        runner = RunnerFactory.create_runner(task, Path("workspace"))
        self.assertIsInstance(runner, LWCRunner)


class TestScoring(unittest.TestCase):
    def test_calculate_pass_rate(self):
        results = [
            TestResult("t1", TestStatus.PASS, 10.0),
            TestResult("t2", TestStatus.PASS, 15.0),
            TestResult("t3", TestStatus.FAIL, 5.0),
            TestResult("t4", TestStatus.TIMEOUT, 20.0),
        ]
        
        stats = calculate_pass_rate(results)
        
        self.assertEqual(stats["total"], 4)
        self.assertEqual(stats["passed"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertEqual(stats["timeout"], 1)
        self.assertEqual(stats["pass_rate"], 50.0)
    
    def test_empty_results(self):
        stats = calculate_pass_rate([])
        
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["pass_rate"], 0.0)


class TestBenchmarkEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.tasks_file = Path(self.temp_dir) / "tasks.json"
        self.workspace_dir = Path(self.temp_dir) / "workspace"
        self.results_dir = Path(self.temp_dir) / "results"
        
        tasks_data = [
            {
                "instance_id": "test-001",
                "task_type": "LWC",
                "repo_url": "https://github.com/test/repo",
                "base_commit": "main",
                "problem_description": "Test",
                "validation": {
                    "command": "npm test",
                    "expected_outcome": "0"
                },
                "timeouts": {
                    "setup": 300,
                    "run": 180
                }
            }
        ]
        
        with open(self.tasks_file, 'w') as f:
            json.dump(tasks_data, f)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_load_tasks(self):
        engine = BenchmarkEngine(
            self.tasks_file,
            self.workspace_dir,
            self.results_dir
        )
        
        engine.load_tasks()
        
        self.assertEqual(len(engine.tasks), 1)
        self.assertEqual(engine.tasks[0].instance_id, "test-001")


if __name__ == '__main__':
    unittest.main()
