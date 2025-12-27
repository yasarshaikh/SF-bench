#!/usr/bin/env python3
"""
Test Gemini Flash model on SF-Bench tasks.

Usage:
    python scripts/test_gemini.py --model gemini-2.0-flash-exp --task-id apex-trigger-handler-001
    python scripts/test_gemini.py --model gemini-1.5-flash --tasks data/tasks/dev.json
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sfbench.engine import BenchmarkEngine
from sfbench import Task
from sfbench.utils.ai_agent import AIAgent
from sfbench.utils.sfdx import verify_devhub


def test_gemini_on_task(
    task: Task,
    api_key: str,
    model_name: str = "gemini-2.0-flash-exp",
    skip_devhub: bool = False
) -> dict:
    """
    Test Gemini on a single task.
    
    Args:
        task: Task to evaluate
        api_key: Google AI Studio API key
        model_name: Gemini model name (gemini-2.0-flash-exp, gemini-1.5-flash, etc.)
        skip_devhub: Skip Dev Hub verification
        
    Returns:
        Result dictionary
    """
    print(f"\n{'='*60}")
    print(f"Testing Gemini {model_name} on Task: {task.instance_id}")
    print(f"Task Type: {task.task_type.value}")
    print(f"Description: {task.problem_description[:200]}...")
    print(f"{'='*60}\n")
    
    # Initialize Gemini agent
    agent = AIAgent(provider="gemini", model=model_name, api_key=api_key)
    
    # Generate solution
    print("🤖 Generating solution with Gemini...")
    try:
        solution = agent.generate_solution(
            task_description=task.problem_description,
            context={
                "task_type": task.task_type.value,
                "instance_id": task.instance_id,
                "repo_url": task.repo_url,
                "base_commit": task.base_commit
            }
        )
        print(f"✓ Solution generated ({len(solution)} characters)")
    except Exception as e:
        print(f"✗ Failed to generate solution: {str(e)}")
        return {
            "task_id": task.instance_id,
            "status": "ERROR",
            "error": str(e),
            "model": model_name
        }
    
    # Save solution
    solutions_dir = Path("solutions/gemini")
    solutions_dir.mkdir(parents=True, exist_ok=True)
    solution_file = solutions_dir / f"{task.instance_id}.patch"
    with open(solution_file, 'w') as f:
        f.write(solution)
    print(f"✓ Solution saved to: {solution_file}")
    
    # Verify Dev Hub if needed
    if not skip_devhub and task.task_type.value in ["APEX", "FLOW", "DEPLOY", "LIGHTNING_PAGE", "PAGE_LAYOUT", "COMMUNITY", "ARCHITECTURE"]:
        print("\nVerifying Dev Hub authentication...")
        if not verify_devhub():
            print("⚠️  Warning: No Dev Hub found. Skipping execution.")
            return {
                "task_id": task.instance_id,
                "status": "SKIPPED",
                "reason": "No Dev Hub",
                "solution_file": str(solution_file),
                "model": model_name
            }
    
    # Evaluate solution
    print("\n🔍 Evaluating solution...")
    workspace_dir = Path("workspace")
    results_dir = Path("results/gemini")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a temporary tasks file for the engine
    temp_tasks_file = results_dir / "temp_tasks.json"
    with open(temp_tasks_file, 'w') as f:
        json.dump([task.to_dict()], f, indent=2)
    
    engine = BenchmarkEngine(
        tasks_file=temp_tasks_file,
        workspace_dir=workspace_dir,
        results_dir=results_dir,
        max_workers=1
    )
    
    # Run single task
    try:
        result = engine.run_single_task(task, solution)
        
        print(f"\n{'='*60}")
        print(f"📊 Evaluation Result:")
        print(f"  Status: {result.status.value}")
        print(f"  Duration: {result.duration:.2f}s")
        if result.error_message:
            print(f"  Error: {result.error_message}")
        if result.details:
            print(f"  Details: {json.dumps(result.details, indent=2)}")
        print(f"{'='*60}\n")
        
        return {
            "task_id": task.instance_id,
            "status": result.status.value,
            "duration": result.duration,
            "error": result.error_message,
            "details": result.details,
            "solution_file": str(solution_file),
            "model": model_name,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"✗ Evaluation failed: {str(e)}")
        return {
            "task_id": task.instance_id,
            "status": "ERROR",
            "error": str(e),
            "solution_file": str(solution_file),
            "model": model_name
        }


def main():
    parser = argparse.ArgumentParser(
        description='Test Gemini Flash on SF-Bench tasks',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--api-key', '-k',
        type=str,
        required=True,
        help='Google AI Studio API key'
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='gemini-2.0-flash-exp',
        help='Gemini model name (default: gemini-2.0-flash-exp). Options: gemini-2.0-flash-exp, gemini-1.5-flash'
    )
    
    parser.add_argument(
        '--task-id', '-t',
        type=str,
        help='Specific task ID to test (e.g., apex-trigger-handler-001)'
    )
    
    parser.add_argument(
        '--tasks', '-f',
        type=str,
        default='data/tasks/dev.json',
        help='Tasks JSON file (default: data/tasks/dev.json)'
    )
    
    parser.add_argument(
        '--skip-devhub',
        action='store_true',
        help='Skip Dev Hub verification'
    )
    
    args = parser.parse_args()
    
    # Load tasks
    tasks_file = Path(args.tasks)
    if not tasks_file.exists():
        print(f"Error: Tasks file not found: {tasks_file}")
        sys.exit(1)
    
    with open(tasks_file, 'r') as f:
        tasks_data = json.load(f)
    
    # Convert to Task objects
    tasks = [Task.from_dict(t) for t in tasks_data]
    
    # Filter by task_id if specified
    if args.task_id:
        tasks = [t for t in tasks if t.instance_id == args.task_id]
        if not tasks:
            print(f"Error: Task ID '{args.task_id}' not found in {tasks_file}")
            sys.exit(1)
    
    # Test on tasks
    results = []
    for task in tasks:
        result = test_gemini_on_task(
            task=task,
            api_key=args.api_key,
            model_name=args.model,
            skip_devhub=args.skip_devhub
        )
        results.append(result)
    
    # Save results
    results_file = Path(f"results/gemini/{args.model.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to: {results_file}")
    
    # Summary
    passed = sum(1 for r in results if r.get("status") == "PASS")
    total = len(results)
    print(f"\n📊 Summary: {passed}/{total} passed ({passed/total*100:.1f}%)" if total > 0 else "\n📊 Summary: No tasks completed")


if __name__ == '__main__':
    main()
