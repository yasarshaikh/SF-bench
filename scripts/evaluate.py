#!/usr/bin/env python3
"""
SF-Bench Evaluation Script

The industry's first comprehensive benchmark for Salesforce AI coding agents.
Validates not just deployment, but actual functionality.

Usage:
    python scripts/evaluate.py --model <model_name> --tasks <task_file>

Example:
    python scripts/evaluate.py --model gpt-4 --tasks data/tasks/verified.json
    python scripts/evaluate.py --model claude-3 --tasks data/tasks/realistic.json --functional
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sfbench.engine import BenchmarkEngine
from sfbench import Task, TaskType
from sfbench.utils.solution_loader import SolutionLoader
from sfbench.utils.sfdx import verify_devhub, create_scratch_org, delete_scratch_org, get_scratch_org_username
from sfbench.utils.ai_agent import AIAgent, create_openrouter_agent, create_gemini_agent, create_routellm_agent
from sfbench.validators.functional_validator import FunctionalValidator, FunctionalValidationResult, ValidationLevel


def run_evaluation(
    model_name: str,
    tasks_file: Path,
    solutions_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    max_workers: int = 3,
    skip_devhub: bool = False,
    functional_validation: bool = False,
    scratch_org_alias: Optional[str] = None,
    provider: Optional[str] = None
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
        functional_validation: Enable full functional validation (requires scratch org)
        scratch_org_alias: Alias for scratch org to use for functional testing
        provider: Explicitly specified AI provider
        
    Returns:
        Evaluation results dictionary
    """
    # Setup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_safe_name = model_name.replace("/", "-").replace(" ", "_")
    
    if output_dir is None:
        output_dir = Path(f"results/{model_safe_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    workspace_dir = Path("workspace")
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    # Verify Dev Hub and create scratch org
    scratch_org_created = False
    if not skip_devhub:
        print("🔐 Verifying Dev Hub authentication...")
        devhub_found = verify_devhub()
        if not devhub_found:
            print("⚠️  Warning: Dev Hub verification failed, but attempting to create scratch org anyway...")
        
        # Try to create scratch org (even if verify_devhub failed - it might still work)
        if not scratch_org_alias:
            scratch_org_alias = f"sfbench-{model_safe_name}-{timestamp}"
            print(f"\n🏗️  Creating scratch org: {scratch_org_alias}")
            try:
                org_info = create_scratch_org(scratch_org_alias, duration_days=1)
                scratch_org_created = True
                org_username = org_info.get('username')
                print(f"✅ Scratch org created: {org_username}")
                # Set as default org for CLI commands
                from sfbench.utils.sfdx import run_sfdx
                run_sfdx(f"sf config set target-org {scratch_org_alias}", timeout=30)
                # Also set by username for compatibility
                if org_username:
                    run_sfdx(f"sf config set target-org {org_username}", timeout=30)
            except Exception as e:
                print(f"❌ Failed to create scratch org: {e}")
                print("   Continuing with existing orgs or local validation only...")
                scratch_org_alias = None
        else:
            print(f"📌 Using existing scratch org: {scratch_org_alias}")
    
    # Initialize engine with scratch org
    engine = BenchmarkEngine(
        tasks_file=tasks_file,
        workspace_dir=workspace_dir,
        results_dir=output_dir,
        max_workers=max_workers,
        scratch_org_alias=scratch_org_alias
    )
    
    # Load tasks first
    print(f"📋 Loading tasks from: {tasks_file}")
    engine.load_tasks(validate=True)
    print(f"✅ Loaded {len(engine.tasks)} tasks")
    
    # Load or generate solutions
    solutions = {}
    if solutions_path:
        solutions = SolutionLoader.load_solutions(solutions_path)
        print(f"📁 Loaded {len(solutions)} solutions from {solutions_path}")
    else:
        # Generate solutions using AI
        print(f"\n🤖 Generating solutions using {model_name}...")
        try:
            # Determine provider
            agent = None
            if provider:
                # Use explicitly specified provider
                if provider.lower() == "routellm":
                    agent = create_routellm_agent(model=model_name)
                elif provider.lower() == "openrouter":
                    agent = create_openrouter_agent(model=model_name)
                elif provider.lower() == "gemini" or provider.lower() == "google":
                    agent = create_gemini_agent(model=model_name)
                elif provider.lower() == "anthropic":
                    from sfbench.utils.ai_agent import create_anthropic_agent
                    agent = create_anthropic_agent(model=model_name)
                elif provider.lower() == "openai":
                    from sfbench.utils.ai_agent import create_openai_agent
                    agent = create_openai_agent(model=model_name)
                elif provider.lower() == "ollama":
                    from sfbench.utils.ai_agent import create_ollama_agent
                    agent = create_ollama_agent(model=model_name)
                else:
                    # Generic fallback using basic constructor
                    agent = AIAgent(provider=provider, model=model_name)
            
            # Auto-detect if no provider specified
            if not agent:
                if "grok" in model_name.lower() or model_name.startswith("gpt-5") or model_name.startswith("claude-sonnet-4") or model_name.startswith("claude-opus-4"):
                    # RouteLLM model (Grok, GPT-5, Claude Sonnet 4, etc.)
                    agent = create_routellm_agent(model=model_name)
                elif model_name.startswith("anthropic/") or model_name.startswith("openai/") or model_name.startswith("meta-llama/"):
                    # OpenRouter model
                    agent = create_openrouter_agent(model=model_name)
                elif "gemini" in model_name.lower():
                    # Gemini model
                    agent = create_gemini_agent(model=model_name)
                else:
                    # Default to OpenRouter
                    agent = create_openrouter_agent(model=model_name)
            
            print(f"   Using provider: {agent.provider}")
            
            for task in engine.tasks:
                print(f"   Generating solution for {task.instance_id}...")
                try:
                    solution = agent.generate_solution(
                        task_description=task.problem_description,
                        context={
                            "repo_url": task.repo_url,
                            "base_commit": task.base_commit,
                            "task_type": task.task_type.value
                        }
                    )
                    solutions[task.instance_id] = solution
                    print(f"   ✅ Generated {len(solution)} chars")
                except Exception as e:
                    print(f"   ❌ Failed: {e}")
                    solutions[task.instance_id] = None
            
            print(f"✅ Generated {len([s for s in solutions.values() if s])} solutions")
        except Exception as e:
            print(f"❌ Failed to generate solutions: {e}")
            print("   Continuing without solutions (will test deployment only)...")
    
    print(f"\n🚀 Running evaluation for: {model_name}")
    if functional_validation:
        print(f"🔬 Functional validation: ENABLED (realistic mode)")
    else:
        print(f"⚡ Functional validation: DISABLED (deployment-only)")
    if scratch_org_alias:
        print(f"🏢 Scratch org: {scratch_org_alias}")
    print(f"📂 Output directory: {output_dir}")
    print("-" * 60)
    
    # Run evaluation
    results = engine.run_all_tasks(solutions if solutions else None)
    
    # Run functional validation BEFORE cleanup (org must still exist!)
    functional_results = []
    if functional_validation and scratch_org_alias:
        print("\n🔬 Running functional validation...")
        try:
            validator = FunctionalValidator(scratch_org_alias, workspace_dir)
            
            for result in results:
                if result.status.value == "PASS":
                    # Get task config
                    task = next((t for t in engine.tasks if t.instance_id == result.task_id), None)
                    if task:
                        repo_dir = workspace_dir / result.task_id
                        
                        try:
                            if task.task_type == TaskType.APEX:
                                func_result = validator.validate_apex(
                                    result.task_id, 
                                    task.__dict__, 
                                    repo_dir
                                )
                            elif task.task_type == TaskType.FLOW:
                                func_result = validator.validate_flow(
                                    result.task_id,
                                    task.__dict__,
                                    repo_dir
                                )
                            elif task.task_type == TaskType.LWC:
                                func_result = validator.validate_lwc(
                                    result.task_id,
                                    task.__dict__,
                                    repo_dir
                                )
                            else:
                                # For other task types, create minimal result
                                func_result = FunctionalValidationResult(
                                    task_id=result.task_id,
                                    validation_level=ValidationLevel.DEPLOYMENT
                                )
                                func_result.deployment_passed = True
                                func_result.calculate_score()
                            
                            functional_results.append(func_result.to_dict())
                            print(f"   ✅ {result.task_id}: Score {func_result.score:.1f}%")
                        except Exception as e:
                            print(f"   ⚠️  {result.task_id}: Functional validation error: {e}")
                            # Create error result
                            error_result = FunctionalValidationResult(
                                task_id=result.task_id,
                                validation_level=ValidationLevel.DEPLOYMENT
                            )
                            error_result.overall_status = "error"
                            error_result.score = 0.0
                            functional_results.append(error_result.to_dict())
        except Exception as e:
            print(f"⚠️  Functional validation failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Cleanup: Delete scratch org AFTER functional validation
    if scratch_org_created and scratch_org_alias:
        print(f"\n🧹 Cleaning up scratch org: {scratch_org_alias}")
        try:
            delete_scratch_org(scratch_org_alias)
            print("✅ Scratch org deleted")
        except Exception as e:
            print(f"⚠️  Warning: Could not delete scratch org: {e}")
    
    # Generate evaluation summary with segment breakdown
    segment_results = calculate_segment_results(results)
    
    evaluation = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "tasks_file": str(tasks_file),
        "validation_mode": "functional" if functional_validation else "deployment",
        "total_tasks": len(results),
        "passed": sum(1 for r in results if r.status.value == "PASS"),
        "failed": sum(1 for r in results if r.status.value == "FAIL"),
        "timeout": sum(1 for r in results if r.status.value == "TIMEOUT"),
        "error": sum(1 for r in results if r.status.value == "ERROR"),
        "pass_rate": 0.0,
        "segment_results": segment_results,
        "functional_validation": functional_results if functional_results else None,
        "results": [r.to_dict() for r in results]
    }
    
    if evaluation["total_tasks"] > 0:
        evaluation["pass_rate"] = round(
            (evaluation["passed"] / evaluation["total_tasks"]) * 100, 2
        )
    
    # Save evaluation
    eval_file = output_dir / f"evaluation_{model_safe_name}_{timestamp}.json"
    with open(eval_file, 'w') as f:
        json.dump(evaluation, f, indent=2)
    
    # Print results
    print_results(evaluation)
    print(f"\n💾 Results saved to: {eval_file}")
    
    return evaluation


def calculate_segment_results(results) -> Dict[str, Dict[str, Any]]:
    """Calculate pass rates by task segment/category."""
    segments = {}
    
    for result in results:
        # Extract task type from ID (e.g., "apex-trigger-001" -> "apex")
        task_id = result.task_id
        if "-" in task_id:
            segment = task_id.split("-")[0].upper()
        else:
            segment = "OTHER"
        
        if segment not in segments:
            segments[segment] = {"total": 0, "passed": 0, "failed": 0, "error": 0}
        
        segments[segment]["total"] += 1
        if result.status.value == "PASS":
            segments[segment]["passed"] += 1
        elif result.status.value == "FAIL":
            segments[segment]["failed"] += 1
        else:
            segments[segment]["error"] += 1
    
    # Calculate pass rates
    for segment in segments:
        total = segments[segment]["total"]
        passed = segments[segment]["passed"]
        segments[segment]["pass_rate"] = round((passed / total) * 100, 1) if total > 0 else 0.0
    
    return segments


def print_results(evaluation: Dict[str, Any]):
    """Print formatted evaluation results."""
    print("\n" + "=" * 60)
    print(f"📊 EVALUATION COMPLETE: {evaluation['model']}")
    print("=" * 60)
    
    # Overall results
    print(f"\n📈 Overall Results:")
    print(f"   Total Tasks: {evaluation['total_tasks']}")
    print(f"   ✅ Passed: {evaluation['passed']}")
    print(f"   ❌ Failed: {evaluation['failed']}")
    print(f"   ⏱️  Timeout: {evaluation['timeout']}")
    print(f"   ⚠️  Error: {evaluation['error']}")
    print(f"   📊 Pass Rate: {evaluation['pass_rate']}%")
    
    # Segment breakdown
    if evaluation.get('segment_results'):
        print(f"\n📋 Results by Segment:")
        print("-" * 40)
        for segment, data in sorted(evaluation['segment_results'].items()):
            status_icon = "✅" if data['pass_rate'] >= 80 else "⚠️" if data['pass_rate'] >= 50 else "❌"
            print(f"   {status_icon} {segment}: {data['pass_rate']}% ({data['passed']}/{data['total']})")
    
    # Functional validation results with detailed scoring
    if evaluation.get('functional_validation'):
        print(f"\n🔬 Functional Validation (Weighted Scoring 0-100):")
        print("-" * 60)
        total_score = 0.0
        scored_count = 0
        for func_result in evaluation['functional_validation']:
            task_id = func_result.get('task_id', 'unknown')
            score = func_result.get('score', 0.0) or 0.0
            status = func_result.get('overall_status', 'unknown')
            
            # Calculate average
            total_score += score
            scored_count += 1
            
            # Display result
            emoji = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
            print(f"  {emoji} {task_id:40s} Score: {score:.1f}% | Status: {status}")
            
            # Show breakdown if available
            checks = []
            if func_result.get('deployment_passed'): checks.append("Deploy(10%)")
            if func_result.get('unit_tests_passed'): checks.append("Unit(20%)")
            if func_result.get('functional_tests_passed'): checks.append("Functional(50%)")
            if func_result.get('bulk_tests_passed'): checks.append("Bulk(10%)")
            if func_result.get('no_manual_tweaks'): checks.append("NoTweaks(10%)")
            if checks:
                print(f"      └─ Passed: {', '.join(checks)}")
        
        if scored_count > 0:
            avg_score = total_score / scored_count
            print(f"\n📊 Average Functional Score: {avg_score:.1f}% (out of 100)")
        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='SF-Bench: The Salesforce AI Coding Benchmark',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick evaluation (deployment only)
  python scripts/evaluate.py --model gpt-4 --tasks data/tasks/verified.json

  # Realistic evaluation (functional validation)
  python scripts/evaluate.py --model claude-3 --tasks data/tasks/realistic.json \\
      --functional --scratch-org my-scratch-org

  # With pre-generated solutions
  python scripts/evaluate.py --model gemini --solutions solutions/gemini/
        """
    )
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        required=True,
        help='Name of the model being evaluated (e.g., gpt-4, claude-3, gemini-2.5-flash)'
    )
    
    parser.add_argument(
        '--provider', '-p',
        type=str,
        help='Explicit AI provider (e.g., routellm, openrouter, gemini)'
    )
    
    parser.add_argument(
        '--tasks', '-t',
        type=str,
        default='data/tasks/verified.json',
        help='Path to tasks JSON file (default: data/tasks/verified.json)'
    )
    
    parser.add_argument(
        '--solutions', '-s',
        type=str,
        help='Path to solutions directory or JSON file'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output directory for results (default: results/<model>/)'
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
    
    parser.add_argument(
        '--functional', '-f',
        action='store_true',
        help='Enable functional validation (requires scratch org)'
    )
    
    parser.add_argument(
        '--scratch-org',
        type=str,
        help='Scratch org alias for functional testing'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    tasks_file = Path(args.tasks)
    if not tasks_file.exists():
        print(f"❌ Error: Tasks file not found: {tasks_file}")
        sys.exit(1)
    
    if args.functional and not args.scratch_org:
        print("⚠️  Warning: --functional requires --scratch-org. Falling back to deployment validation.")
    
    solutions_path = Path(args.solutions) if args.solutions else None
    output_dir = Path(args.output) if args.output else None
    
    # Run evaluation
    run_evaluation(
        model_name=args.model,
        tasks_file=tasks_file,
        solutions_path=solutions_path,
        output_dir=output_dir,
        max_workers=args.max_workers,
        skip_devhub=args.skip_devhub,
        functional_validation=args.functional,
        scratch_org_alias=args.scratch_org,
        provider=args.provider
    )


if __name__ == '__main__':
    main()
