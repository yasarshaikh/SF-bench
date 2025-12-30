"""
SF-Bench Automated Reporting

Generates professional reports in multiple formats:
- JSON: Machine-readable results
- Markdown: Human-readable summaries
- Console: Live progress updates

Inspired by SWE-bench's automated reporting system.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .schema import (
    EvaluationReport,
    InstanceResult,
    TaskStatus,
    ComponentStatus,
)


def make_run_report(
    report: EvaluationReport,
    output_dir: str,
    include_markdown: bool = True,
    include_json: bool = True,
) -> Dict[str, str]:
    """
    Generate comprehensive evaluation report.
    
    Args:
        report: EvaluationReport object
        output_dir: Directory to save reports
        include_markdown: Generate markdown summary
        include_json: Generate JSON report
    
    Returns:
        Dictionary mapping format to file path
    """
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Finalize report (calculate summary)
    report.finalize()
    
    generated_files = {}
    
    # Generate JSON report
    if include_json:
        json_file = output_path / "report.json"
        with open(json_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        generated_files['json'] = str(json_file)
    
    # Generate Markdown summary
    if include_markdown:
        md_file = output_path / "summary.md"
        markdown = generate_markdown_summary(report)
        with open(md_file, 'w') as f:
            f.write(markdown)
        generated_files['markdown'] = str(md_file)
    
    return generated_files


def generate_markdown_summary(report: EvaluationReport) -> str:
    """
    Generate a markdown summary of evaluation results.
    
    Args:
        report: EvaluationReport object
    
    Returns:
        Markdown formatted string
    """
    summary = report.summary
    
    # Header (SWE-bench style)
    md = f"""# SF-Bench Evaluation Report

**Model:** {report.model_name}  
**Dataset:** {report.dataset}  
**Run ID:** {report.run_id}  
**Date:** {datetime.fromisoformat(report.start_time).strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## 📊 Overall Results (SWE-bench Compatible)

| Metric | Value |
|--------|-------|
| **Total Instances** | {summary.total_instances} |
| **Instances Submitted** | {getattr(summary, 'instances_submitted', summary.total_instances)} |
| **Instances Completed** | {getattr(summary, 'instances_completed', summary.total_instances - summary.error_instances)} |
| **Instances Resolved** | {summary.resolved_instances} ✅ |
| **Instances Unresolved** | {getattr(summary, 'instances_unresolved', summary.failed_instances)} |
| **Instances Error** | {summary.error_instances} ⚠️ |
| **Instances Empty Patch** | {getattr(summary, 'instances_empty_patch', 0)} |
| **Resolution Rate** | {getattr(summary, 'resolution_rate', summary.resolve_rate * 100):.1f}% |

---

## 🎯 Scoring Summary

| Metric | Value |
|--------|-------|
| **Average Score** | {summary.avg_score:.1f}/100 |
| **Average Functional Score** | {getattr(summary, 'avg_functional_score', 0):.1f}/50 |
| **Median Score** | {summary.median_score:.1f}/100 |
| **Min Score** | {summary.min_score}/100 |
| **Max Score** | {summary.max_score}/100 |

---

## 🔍 Component Analysis

| Component | Pass Rate | Max Points |
|-----------|-----------|------------|
| **Deployment** | {summary.deployment_pass_rate * 100:.1f}% | 10 |
| **Unit Tests** | {summary.unit_test_pass_rate * 100:.1f}% | 20 |
| **Functional Validation** | {summary.functional_pass_rate * 100:.1f}% | 50 |
| **Bulk Data** | {summary.bulk_pass_rate * 100:.1f}% | 10 |
| **No Manual Tweaks** | {summary.no_tweaks_pass_rate * 100:.1f}% | 10 |

---

## ⏱️ Performance

| Metric | Value |
|--------|-------|
| **Average Duration** | {summary.avg_duration_seconds:.1f}s |
| **Total Duration** | {format_duration(summary.total_duration_seconds)} |

---

## 📋 Task Results (SWE-bench Style)

### Resolved Tasks ({len([i for i in report.instances if i.resolved])})
{chr(10).join(f"- ✅ {inst.instance_id}" for inst in sorted(report.instances, key=lambda x: x.instance_id) if inst.resolved) if any(i.resolved for i in report.instances) else "*None*"}

### Unresolved Tasks ({len([i for i in report.instances if not i.resolved and i.status.value == 'fail'])})
{chr(10).join(f"- ❌ {inst.instance_id}" for inst in sorted(report.instances, key=lambda x: x.instance_id) if not inst.resolved and inst.status.value == 'fail') if any(not i.resolved and i.status.value == 'fail' for i in report.instances) else "*None*"}

### Error Tasks ({len([i for i in report.instances if i.status.value == 'error'])})
{chr(10).join(f"- ⚠️ {inst.instance_id}" for inst in sorted(report.instances, key=lambda x: x.instance_id) if inst.status.value == 'error') if any(i.status.value == 'error' for i in report.instances) else "*None*"}

---

## 📋 Detailed Task Results

"""
    
    # Add individual task results
    for instance in sorted(report.instances, key=lambda x: x.validation.total_score, reverse=True):
        status_emoji = {
            TaskStatus.RESOLVED: "✅",
            TaskStatus.FAIL: "❌",
            TaskStatus.ERROR: "⚠️",
            TaskStatus.SKIPPED: "⏭️",
        }.get(instance.status, "❓")
        
        md += f"### {status_emoji} {instance.instance_id}\n\n"
        md += f"**Status:** {instance.status.value.upper()}  \n"
        md += f"**Score:** {instance.validation.total_score}/100  \n"
        
        if instance.resolved:
            md += f"**Duration:** {instance.duration_seconds:.1f}s  \n"
        
        md += "\n**Component Scores:**\n\n"
        md += "| Component | Status | Points |\n"
        md += "|-----------|--------|--------|\n"
        
        v = instance.validation
        md += f"| Deployment | {component_emoji(v.deployment_status)} {v.deployment_status.value} | {v.deployment_points}/10 |\n"
        md += f"| Unit Tests | {component_emoji(v.unit_test_status)} {v.unit_test_status.value} | {v.unit_test_points}/20 |\n"
        md += f"| Functional | {component_emoji(v.functional_status)} {v.functional_status.value} | {v.functional_points}/50 |\n"
        md += f"| Bulk Data | {component_emoji(v.bulk_status)} {v.bulk_status.value} | {v.bulk_points}/10 |\n"
        md += f"| No Tweaks | {component_emoji(v.no_tweaks_status)} {v.no_tweaks_status.value} | {v.no_tweaks_points}/10 |\n"
        
        if instance.error_message:
            md += f"\n**Error:** {instance.error_message}\n"
        
        md += "\n---\n\n"
    
    # Footer
    md += f"""
## 📈 Interpretation

### Success Criteria

A task is considered **RESOLVED** if:
- ✅ Code deploys successfully
- ✅ Unit tests pass
- ✅ Functional validation passes (business outcome achieved)
- ✅ Total score ≥ 80/100

### Scoring Breakdown

- **Deploy (10%):** Code deploys without errors
- **Unit Tests (20%):** All tests pass
- **Functional (50%):** Business requirement met (most important!)
- **Bulk (10%):** Handles 200+ records
- **No Tweaks (10%):** Works without manual fixes

### Key Insight

A high score means the AI model can:
1. Understand Salesforce-specific requirements
2. Generate correct Apex/Flow/LWC code
3. Meet real business outcomes (not just syntax)

---

**Report Generated:** {datetime.utcnow().isoformat()}  
**SF-Bench Version:** 1.0.0  
**Schema Version:** {report.schema_version}

---

*To reproduce these results:*
```bash
python scripts/evaluate.py --model "{report.model_name}" --tasks data/tasks/{report.dataset}.json
```
"""
    
    return md


def component_emoji(status: ComponentStatus) -> str:
    """Get emoji for component status."""
    return {
        ComponentStatus.PASS: "✅",
        ComponentStatus.FAIL: "❌",
        ComponentStatus.ERROR: "⚠️",
        ComponentStatus.SKIPPED: "⏭️",
    }.get(status, "❓")


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def print_progress_summary(report: EvaluationReport):
    """
    Print a live progress summary to console.
    
    This is called during evaluation to show real-time progress.
    """
    summary = report.summary
    
    print("\n" + "=" * 60)
    print(f"  SF-Bench Evaluation Progress")
    print("=" * 60)
    print(f"  Model: {report.model_name}")
    print(f"  Progress: {len(report.instances)}/{summary.total_instances} tasks")
    
    if summary.total_instances > 0:
        completed = summary.resolved_instances + summary.failed_instances + summary.error_instances
        progress_pct = (completed / summary.total_instances) * 100
        print(f"  Completed: {progress_pct:.1f}%")
        print(f"  Success Rate: {summary.resolve_rate * 100:.1f}%")
        print(f"  Average Score: {summary.avg_score:.1f}/100")
    
    print("=" * 60 + "\n")


def generate_leaderboard_entry(report: EvaluationReport) -> Dict[str, Any]:
    """
    Generate a leaderboard entry from evaluation report.
    
    This creates a standardized entry for the leaderboard.
    
    Args:
        report: EvaluationReport object
    
    Returns:
        Dictionary with leaderboard data
    """
    summary = report.summary
    
    return {
        "model": report.model_name,
        "date": datetime.fromisoformat(report.start_time).strftime('%Y-%m-%d'),
        "dataset": report.dataset,
        "tasks_total": summary.total_instances,
        "tasks_resolved": summary.resolved_instances,
        "resolve_rate": round(summary.resolve_rate * 100, 1),
        "avg_score": round(summary.avg_score, 1),
        "deployment_pass": round(summary.deployment_pass_rate * 100, 1),
        "unit_test_pass": round(summary.unit_test_pass_rate * 100, 1),
        "functional_pass": round(summary.functional_pass_rate * 100, 1),
        "run_id": report.run_id,
    }


def save_leaderboard_entry(report: EvaluationReport, leaderboard_file: str = "docs/LEADERBOARD.md"):
    """
    Append evaluation results to leaderboard.
    
    Args:
        report: EvaluationReport object
        leaderboard_file: Path to leaderboard markdown file
    """
    entry = generate_leaderboard_entry(report)
    
    # Read existing leaderboard
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, 'r') as f:
            content = f.read()
    else:
        content = "# SF-Bench Leaderboard\n\n"
    
    # Format new entry
    new_row = (
        f"| {entry['model']} | {entry['date']} | {entry['resolve_rate']}% | "
        f"{entry['avg_score']}/100 | {entry['deployment_pass']}% | "
        f"{entry['unit_test_pass']}% | {entry['functional_pass']}% |\n"
    )
    
    # Append to leaderboard
    # (In production, this would parse and insert in sorted order)
    with open(leaderboard_file, 'a') as f:
        f.write(new_row)


def export_for_research(report: EvaluationReport, output_file: str):
    """
    Export evaluation data in research-friendly format.
    
    This generates a CSV or JSON suitable for academic analysis.
    
    Args:
        report: EvaluationReport object
        output_file: Path to output file (.csv or .json)
    """
    if output_file.endswith('.json'):
        # Export as JSON
        with open(output_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
    
    elif output_file.endswith('.csv'):
        # Export as CSV
        import csv
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'instance_id', 'model', 'status', 'resolved', 'score',
                'deploy', 'unit_test', 'functional', 'bulk', 'no_tweaks',
                'duration_seconds'
            ])
            
            # Data rows
            for instance in report.instances:
                v = instance.validation
                writer.writerow([
                    instance.instance_id,
                    instance.model_name,
                    instance.status.value,
                    instance.resolved,
                    v.total_score,
                    v.deployment_points,
                    v.unit_test_points,
                    v.functional_points,
                    v.bulk_points,
                    v.no_tweaks_points,
                    instance.duration_seconds,
                ])


def compare_reports(report1: EvaluationReport, report2: EvaluationReport) -> str:
    """
    Generate a comparison markdown between two evaluation reports.
    
    Useful for comparing different models or model versions.
    
    Args:
        report1: First evaluation report
        report2: Second evaluation report
    
    Returns:
        Markdown formatted comparison
    """
    s1 = report1.summary
    s2 = report2.summary
    
    md = f"""# Model Comparison

## Models

- **Model 1:** {report1.model_name}
- **Model 2:** {report2.model_name}

## Overall Results

| Metric | {report1.model_name} | {report2.model_name} | Difference |
|--------|----------|----------|------------|
| Success Rate | {s1.resolve_rate * 100:.1f}% | {s2.resolve_rate * 100:.1f}% | {(s2.resolve_rate - s1.resolve_rate) * 100:+.1f}% |
| Average Score | {s1.avg_score:.1f} | {s2.avg_score:.1f} | {s2.avg_score - s1.avg_score:+.1f} |
| Tasks Resolved | {s1.resolved_instances}/{s1.total_instances} | {s2.resolved_instances}/{s2.total_instances} | {s2.resolved_instances - s1.resolved_instances:+d} |

## Component Performance

| Component | {report1.model_name} | {report2.model_name} | Difference |
|-----------|----------|----------|------------|
| Deployment | {s1.deployment_pass_rate * 100:.1f}% | {s2.deployment_pass_rate * 100:.1f}% | {(s2.deployment_pass_rate - s1.deployment_pass_rate) * 100:+.1f}% |
| Unit Tests | {s1.unit_test_pass_rate * 100:.1f}% | {s2.unit_test_pass_rate * 100:.1f}% | {(s2.unit_test_pass_rate - s1.unit_test_pass_rate) * 100:+.1f}% |
| Functional | {s1.functional_pass_rate * 100:.1f}% | {s2.functional_pass_rate * 100:.1f}% | {(s2.functional_pass_rate - s1.functional_pass_rate) * 100:+.1f}% |

## Performance

| Metric | {report1.model_name} | {report2.model_name} | Difference |
|--------|----------|----------|------------|
| Avg Duration | {s1.avg_duration_seconds:.1f}s | {s2.avg_duration_seconds:.1f}s | {s2.avg_duration_seconds - s1.avg_duration_seconds:+.1f}s |

"""
    
    return md
