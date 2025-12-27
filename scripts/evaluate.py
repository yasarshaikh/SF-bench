#!/usr/bin/env python3
"""
SF-Bench Evaluation Script

This is the main entry point for running evaluations.
Usage:
    python scripts/evaluate.py --model <model_name> --tasks <task_file>

Example:
    python scripts/evaluate.py --model gpt-4 --tasks data/tasks/dev.json
    python scripts/evaluate.py --model claude-3 --tasks data/tasks/full.json --output results/claude-3/
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sfbench.engine import BenchmarkEngine
from sfbench import Task
from sfbench.utils.solution_loader import SolutionLoader
from sfbench.utils.sfdx import verify_devhub


def run_evaluation(
    model_name: str,
    tasks_file: Path,
    solutions_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    max_workers: int = 3,
    skip_devhub: bool = False
) -> Dict[str, Any]:
    """
    Run a complete evaluation for a model.
    
    Args:
        model_name: Name of the model being evaluated
        tasks_file: Path to tasks JSON file
        solutions_path: Path to solutions directory or JSON file
        output_dir: Output directory for results
        max_workers: Maximum parallel workers
        skip_devhub: Skip Dev Hub verification
        
    Returns:
        Evaluation results dictionary
    """
    # Setup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_dir is None:
        output_dir = Path(f"results/{model_name}/{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    workspace_dir = Path("workspace")
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    # Verify Dev Hub if needed
    if not skip_devhub:
        print("Verifying Dev Hub authentication...")
        if not verify_devhub():
            print("Warning: No Dev Hub found. Apex/Deploy tasks may fail.")
    
    # Load solutions
    solutions = {}
    if solutions_path:
        solutions = SolutionLoader.load_solutions(solutions_path)
        print(f"Loaded {len(solutions)} solutions")
    
    # Initialize engine
    engine = BenchmarkEngine(
        tasks_file=tasks_file,
        workspace_dir=workspace_dir,
        results_dir=output_dir,
        max_workers=max_workers
    )
    
    # Load and run tasks
    print(f"Loading tasks from: {tasks_file}")
    engine.load_tasks(validate=True)
    print(f"Loaded {len(engine.tasks)} tasks")
    
    print(f"\nRunning evaluation for: {model_name}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)
    
    results = engine.run_all_tasks(solutions if solutions else None)
    
    # Generate evaluation summary
    evaluation = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "tasks_file": str(tasks_file),
        "total_tasks": len(results),
        "passed": sum(1 for r in results if r.status.value == "PASS"),
        "failed": sum(1 for r in results if r.status.value == "FAIL"),
        "timeout": sum(1 for r in results if r.status.value == "TIMEOUT"),
        "error": sum(1 for r in results if r.status.value == "ERROR"),
        "pass_rate": 0.0,
        "results": [r.to_dict() for r in results]
    }
    
    if evaluation["total_tasks"] > 0:
        evaluation["pass_rate"] = round(
            (evaluation["passed"] / evaluation["total_tasks"]) * 100, 2
        )
    
    # Save evaluation
    eval_file = output_dir / "evaluation.json"
    with open(eval_file, 'w') as f:
        json.dump(evaluation, f, indent=2)
    
    print("\n" + "=" * 60)
    print(f"EVALUATION COMPLETE: {model_name}")
    print("=" * 60)
    print(f"Total Tasks: {evaluation['total_tasks']}")
    print(f"Passed: {evaluation['passed']}")
    print(f"Failed: {evaluation['failed']}")
    print(f"Timeout: {evaluation['timeout']}")
    print(f"Error: {evaluation['error']}")
    print(f"Pass Rate: {evaluation['pass_rate']}%")
    print(f"\nResults saved to: {eval_file}")
    
    return evaluation


def main():
    parser = argparse.ArgumentParser(
        description='SF-Bench: Evaluate AI models on Salesforce tasks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/evaluate.py --model gpt-4 --tasks data/tasks/dev.json
  python scripts/evaluate.py --model claude-3 --solutions solutions/claude-3/
  python scripts/evaluate.py --model gemini --tasks data/tasks/full.json --output results/gemini/
        """
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        required=True,
        help='Name of the model being evaluated (e.g., gpt-4, claude-3)'
    )
    
    parser.add_argument(
        '--tasks', '-t',
        type=str,
        default='data/tasks/dev.json',
        help='Path to tasks JSON file (default: data/tasks/dev.json)'
    )
    
    parser.add_argument(
        '--solutions', '-s',
        type=str,
        help='Path to solutions directory or JSON file'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for results (default: results/<model>/<timestamp>)'
    )
    
    parser.add_argument(
        '--max-workers', '-w',
        type=int,
        default=3,
        help='Maximum parallel workers (default: 3)'
    )
    
    parser.add_argument(
        '--skip-devhub',
        action='store_true',
        help='Skip Dev Hub verification'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    tasks_file = Path(args.tasks)
    if not tasks_file.exists():
        print(f"Error: Tasks file not found: {tasks_file}")
        sys.exit(1)
    
    solutions_path = Path(args.solutions) if args.solutions else None
    output_dir = Path(args.output) if args.output else None
    
    # Run evaluation
    run_evaluation(
        model_name=args.model,
        tasks_file=tasks_file,
        solutions_path=solutions_path,
        output_dir=output_dir,
        max_workers=args.max_workers,
        skip_devhub=args.skip_devhub
    )


if __name__ == '__main__':
    main()

