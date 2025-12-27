import argparse
import sys
from pathlib import Path

from sfbench.engine import BenchmarkEngine
from sfbench.utils.sfdx import verify_devhub
from sfbench.utils.solution_loader import SolutionLoader


def main():
    parser = argparse.ArgumentParser(
        description='SF-Bench: Salesforce Engineering Benchmark Harness'
    )
    
    parser.add_argument(
        '--tasks',
        type=str,
        default='data/tasks/dev.json',
        help='Path to tasks JSON file (default: data/tasks/dev.json)'
    )
    
    parser.add_argument(
        '--workspace',
        type=str,
        default='workspace',
        help='Path to workspace directory (default: workspace)'
    )
    
    parser.add_argument(
        '--results',
        type=str,
        default='results',
        help='Path to results directory (default: results)'
    )
    
    parser.add_argument(
        '--max-workers',
        type=int,
        default=3,
        help='Maximum number of parallel workers (default: 3)'
    )
    
    parser.add_argument(
        '--task-id',
        type=str,
        help='Run a specific task by instance_id'
    )
    
    parser.add_argument(
        '--skip-devhub-check',
        action='store_true',
        help='Skip Dev Hub authentication verification'
    )
    
    parser.add_argument(
        '--solution-dir',
        type=str,
        help='Directory containing solution patches (.patch or .diff files)'
    )
    
    parser.add_argument(
        '--solution-file',
        type=str,
        help='JSON file containing solutions (mapping task_id to patch)'
    )
    
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip task schema validation (use with caution)'
    )
    
    args = parser.parse_args()
    
    tasks_file = Path(args.tasks)
    workspace_dir = Path(args.workspace)
    results_dir = Path(args.results)
    
    if not tasks_file.exists():
        print(f"Error: Tasks file not found: {tasks_file}")
        sys.exit(1)
    
    if not args.skip_devhub_check:
        print("Verifying Dev Hub authentication...")
        if not verify_devhub():
            print("Error: No authenticated Dev Hub found.")
            print("Please authenticate to a Dev Hub using: sf org login web --set-default-dev-hub")
            sys.exit(1)
        print("Dev Hub verified ✓")
    
    workspace_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    engine = BenchmarkEngine(
        tasks_file=tasks_file,
        workspace_dir=workspace_dir,
        results_dir=results_dir,
        max_workers=args.max_workers
    )
    
    print(f"Loading tasks from: {tasks_file}")
    engine.load_tasks(validate=not args.skip_validation)
    print(f"Loaded {len(engine.tasks)} task(s)")
    
    # Load solutions if provided
    solutions = {}
    if args.solution_dir:
        solution_path = Path(args.solution_dir)
        solutions = SolutionLoader.load_solutions(solution_path)
        print(f"Loaded {len(solutions)} solution(s) from directory: {solution_path}")
    elif args.solution_file:
        solution_path = Path(args.solution_file)
        solutions = SolutionLoader.load_solutions(solution_path)
        print(f"Loaded {len(solutions)} solution(s) from file: {solution_path}")
    
    if args.task_id:
        task = next((t for t in engine.tasks if t.instance_id == args.task_id), None)
        if not task:
            print(f"Error: Task not found: {args.task_id}")
            sys.exit(1)
        
        print(f"\nRunning single task: {args.task_id}")
        patch = solutions.get(args.task_id)
        if patch:
            print(f"Using provided solution for {args.task_id}")
        result = engine.run_single_task(task, patch)
        print(f"\nResult: {result.status.value}")
        print(f"Duration: {result.duration:.2f}s")
        if result.error_message:
            print(f"Error: {result.error_message}")
    else:
        print(f"\nRunning all tasks with max {args.max_workers} workers...")
        engine.run_all_tasks(solutions if solutions else None)
    
    print("\nBenchmark complete!")


if __name__ == '__main__':
    main()
