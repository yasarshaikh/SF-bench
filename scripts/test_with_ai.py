"""
Test script to evaluate SF-Bench with a real AI model.
This script demonstrates end-to-end evaluation of an AI agent on Salesforce tasks.
"""
import sys
from pathlib import Path
import json

# Add harness to path
sys.path.insert(0, str(Path(__file__).parent))

from sfbench.engine import BenchmarkEngine
from sfbench import Task, TaskType
from sfbench.utils.ai_agent import AIAgent, FreeTierAIAgent
from sfbench.utils.sfdx import verify_devhub


def test_ai_on_task(task: Task, ai_provider: str = "local") -> dict:
    """
    Test an AI agent on a single task.
    
    Args:
        task: Task to evaluate
        ai_provider: AI provider to use ("local", "huggingface", "openai", "anthropic")
        
    Returns:
        Result dictionary with solution and evaluation
    """
    print(f"\n{'='*60}")
    print(f"Testing AI Agent on Task: {task.instance_id}")
    print(f"Task Type: {task.task_type.value}")
    print(f"Description: {task.problem_description}")
    print(f"{'='*60}\n")
    
    # Initialize AI agent
    if ai_provider == "local":
        agent = FreeTierAIAgent.create_agent("local")
    elif ai_provider == "huggingface":
        agent = FreeTierAIAgent.create_agent("huggingface")
    else:
        agent = AIAgent(provider=ai_provider, model="gpt-3.5-turbo")
    
    # Generate solution
    print("Generating solution with AI agent...")
    try:
        solution = agent.generate_solution(
            task_description=task.problem_description,
            context={
                "task_type": task.task_type.value,
                "instance_id": task.instance_id
            }
        )
        print(f"✓ Solution generated ({len(solution)} characters)")
    except Exception as e:
        print(f"✗ Failed to generate solution: {str(e)}")
        return {
            "task_id": task.instance_id,
            "status": "ERROR",
            "error": str(e)
        }
    
    # Save solution for inspection
    solutions_dir = Path("solutions")
    solutions_dir.mkdir(exist_ok=True)
    solution_file = solutions_dir / f"{task.instance_id}.patch"
    with open(solution_file, 'w') as f:
        f.write(solution)
    print(f"✓ Solution saved to: {solution_file}")
    
    # Evaluate solution
    print("\nEvaluating solution...")
    workspace_dir = Path("workspace")
    results_dir = Path("results")
    
    engine = BenchmarkEngine(
        tasks_file=Path("data/tasks.json"),
        workspace_dir=workspace_dir,
        results_dir=results_dir,
        max_workers=1
    )
    
    # Create a single-task engine
    result = engine.run_single_task(task, solution)
    
    print(f"\n{'='*60}")
    print(f"Evaluation Result:")
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
        "solution_file": str(solution_file)
    }


def main():
    """Main test function."""
    print("SF-Bench AI Agent Test")
    print("=" * 60)
    
    # Check Dev Hub (skip for LWC-only tests)
    print("Checking prerequisites...")
    if not verify_devhub():
        print("Warning: No Dev Hub found. Some tasks may fail.")
        print("Continue anyway? (y/n): ", end="")
        response = input().strip().lower()
        if response != 'y':
            print("Exiting.")
            return
    
    # Load tasks
    tasks_file = Path("data/tasks.json")
    if not tasks_file.exists():
        print(f"Error: Tasks file not found: {tasks_file}")
        return
    
    with open(tasks_file, 'r') as f:
        tasks_data = json.load(f)
    
    tasks = [Task.from_dict(t) for t in tasks_data]
    
    # Select AI provider
    print("\nSelect AI Provider:")
    print("  1. Local (template/placeholder)")
    print("  2. Hugging Face (free tier)")
    print("  3. OpenAI (requires API key)")
    print("  4. Anthropic (requires API key)")
    print("\nEnter choice (1-4, default=1): ", end="")
    
    choice = input().strip()
    provider_map = {
        "1": "local",
        "2": "huggingface",
        "3": "openai",
        "4": "anthropic"
    }
    provider = provider_map.get(choice, "local")
    
    # Select task
    print(f"\nAvailable tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"  {i}. {task.instance_id} ({task.task_type.value})")
    print(f"  {len(tasks) + 1}. All tasks")
    print(f"\nEnter choice (1-{len(tasks) + 1}, default=1): ", end="")
    
    task_choice = input().strip()
    
    results = []
    
    if task_choice == str(len(tasks) + 1) or task_choice == "":
        # Test all tasks
        print(f"\nTesting all {len(tasks)} tasks with {provider}...")
        for task in tasks:
            result = test_ai_on_task(task, provider)
            results.append(result)
    else:
        # Test single task
        try:
            task_idx = int(task_choice) - 1
            if 0 <= task_idx < len(tasks):
                task = tasks[task_idx]
                result = test_ai_on_task(task, provider)
                results.append(result)
            else:
                print("Invalid task selection.")
                return
        except ValueError:
            print("Invalid input.")
            return
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for result in results:
        print(f"  {result['task_id']}: {result['status']} ({result.get('duration', 0):.2f}s)")
    print("=" * 60)
    
    # Save results
    results_file = Path("results/ai_test_results.json")
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()

