#!/usr/bin/env python3
"""
SF-Bench Leaderboard Generator

Generates leaderboard from evaluation results.
Usage:
    python scripts/leaderboard.py --results-dir results/ --output leaderboard.json
"""
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def load_evaluations(results_dir: Path) -> List[Dict[str, Any]]:
    """Load all evaluation results from a directory."""
    evaluations = []
    
    # Look for evaluation.json files recursively
    for eval_file in results_dir.rglob("evaluation.json"):
        try:
            with open(eval_file, 'r') as f:
                data = json.load(f)
                data['_file'] = str(eval_file)
                evaluations.append(data)
        except Exception as e:
            print(f"Warning: Failed to load {eval_file}: {e}")
    
    return evaluations


def generate_leaderboard(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate leaderboard from evaluations."""
    
    # Group by model, keep best result
    model_results = {}
    
    for eval_data in evaluations:
        model = eval_data.get('model', 'unknown')
        pass_rate = eval_data.get('pass_rate', 0.0)
        
        if model not in model_results or pass_rate > model_results[model]['pass_rate']:
            model_results[model] = {
                'model': model,
                'pass_rate': pass_rate,
                'passed': eval_data.get('passed', 0),
                'total': eval_data.get('total_tasks', 0),
                'failed': eval_data.get('failed', 0),
                'timeout': eval_data.get('timeout', 0),
                'error': eval_data.get('error', 0),
                'timestamp': eval_data.get('timestamp', ''),
                'tasks_file': eval_data.get('tasks_file', '')
            }
    
    # Sort by pass rate (descending)
    ranked = sorted(model_results.values(), key=lambda x: x['pass_rate'], reverse=True)
    
    # Add rank
    for i, entry in enumerate(ranked, 1):
        entry['rank'] = i
    
    leaderboard = {
        'generated_at': datetime.now().isoformat(),
        'total_models': len(ranked),
        'entries': ranked
    }
    
    return leaderboard


def generate_markdown_table(leaderboard: Dict[str, Any]) -> str:
    """Generate markdown table from leaderboard."""
    lines = [
        "# SF-Bench Leaderboard",
        "",
        f"*Last updated: {leaderboard['generated_at'][:10]}*",
        "",
        "| Rank | Model | Pass Rate | Passed | Total | Failed | Timeout | Error |",
        "|------|-------|-----------|--------|-------|--------|---------|-------|"
    ]
    
    for entry in leaderboard['entries']:
        lines.append(
            f"| {entry['rank']} | {entry['model']} | {entry['pass_rate']}% | "
            f"{entry['passed']} | {entry['total']} | {entry['failed']} | "
            f"{entry['timeout']} | {entry['error']} |"
        )
    
    lines.extend([
        "",
        "---",
        "",
        "## How to Submit",
        "",
        "1. Run your model on SF-Bench tasks",
        "2. Submit results via pull request",
        "3. Results will be verified and added to leaderboard",
        "",
        "See [CONTRIBUTING.md](../CONTRIBUTING.md) for details."
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate SF-Bench leaderboard from evaluation results'
    )
    
    parser.add_argument(
        '--results-dir', '-r',
        type=str,
        default='results',
        help='Directory containing evaluation results (default: results)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='leaderboard.json',
        help='Output file for leaderboard JSON (default: leaderboard.json)'
    )
    
    parser.add_argument(
        '--markdown', '-md',
        type=str,
        help='Output file for markdown table (optional)'
    )
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        return
    
    # Load evaluations
    print(f"Loading evaluations from: {results_dir}")
    evaluations = load_evaluations(results_dir)
    print(f"Found {len(evaluations)} evaluation(s)")
    
    if not evaluations:
        print("No evaluations found. Run evaluate.py first.")
        return
    
    # Generate leaderboard
    leaderboard = generate_leaderboard(evaluations)
    
    # Save JSON
    output_file = Path(args.output)
    with open(output_file, 'w') as f:
        json.dump(leaderboard, f, indent=2)
    print(f"Leaderboard saved to: {output_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("LEADERBOARD")
    print("=" * 60)
    for entry in leaderboard['entries']:
        print(f"#{entry['rank']} {entry['model']}: {entry['pass_rate']}%")
    
    # Save markdown if requested
    if args.markdown:
        md_content = generate_markdown_table(leaderboard)
        md_file = Path(args.markdown)
        with open(md_file, 'w') as f:
            f.write(md_content)
        print(f"\nMarkdown saved to: {md_file}")


if __name__ == '__main__':
    main()

