---
layout: default
title: Result Schema Reference
description: Complete reference for SF-Bench result schema v2
---

# Result Schema Reference

Complete reference for SF-Bench result schema v2 format.

---

## Schema Version

**Current Version:** 2.0  
**Previous Version:** 1.0 (legacy format, still supported)

---

## Top-Level Structure

```json
{
  "schema_version": "2.0",
  "run_id": "claude-sonnet-4.5-20251229_143000",
  "model_name": "anthropic/claude-3.5-sonnet",
  "dataset": "verified",
  "config": {...},
  "instances": [...],
  "summary": {...},
  "start_time": "2025-12-29T14:30:00Z",
  "end_time": "2025-12-29T16:45:00Z",
  "environment": {...}
}
```

---

## Fields

### `schema_version` (string, required)
Schema version identifier. Current: `"2.0"`

### `run_id` (string, required)
Unique identifier for this evaluation run.
Format: `<model-name>-<timestamp>`

### `model_name` (string, required)
Name of the AI model being evaluated.
Examples: `"anthropic/claude-3.5-sonnet"`, `"gemini-2.5-flash"`

### `dataset` (string, required)
Dataset used for evaluation.
Options: `"verified"`, `"lite"`, `"full"`, or custom name

### `config` (object, required)
Evaluation configuration.

```json
{
  "tasks_file": "data/tasks/verified.json",
  "validation_mode": "functional",
  "max_workers": 2,
  "functional_validation": true,
  "scratch_org_alias": "sfbench-claude-sonnet-4.5-20251229"
}
```

### `instances` (array, required)
Array of `InstanceResult` objects (one per task).

### `summary` (object, required)
Summary statistics. See [Summary Object](#summary-object) below.

### `start_time` (string, required)
ISO 8601 timestamp when evaluation started.

### `end_time` (string, optional)
ISO 8601 timestamp when evaluation completed.

### `environment` (object, optional)
Environment information (CLI version, Python version, etc.)

---

## Instance Result

Represents the result of evaluating one task.

```json
{
  "instance_id": "lwc-component-001",
  "model_name": "anthropic/claude-3.5-sonnet",
  "status": "resolved",
  "resolved": true,
  "validation": {...},
  "duration_seconds": 245.3,
  "scratch_org_username": "test-abc123@example.com",
  "error_message": null,
  "error_type": null,
  "start_time": "2025-12-29T14:30:15Z",
  "end_time": "2025-12-29T14:34:20Z",
  "log_path": "logs/run_evaluation/claude-sonnet-4.5-20251229/lwc-component-001/run_instance.log",
  "solution_patch": "diff --git a/..."
}
```

### Status Values

- `"resolved"`: Task successfully completed (score ≥80, all critical components pass)
- `"fail"`: Task failed validation
- `"error"`: Error during execution
- `"skipped"`: Task was not executed

---

## Validation Breakdown

Detailed validation results for each component.

```json
{
  "deployment_status": "pass",
  "deployment_message": "Deployed successfully",
  "deployment_points": 10,
  
  "unit_test_status": "pass",
  "unit_test_message": "All tests passed",
  "unit_test_passed": 15,
  "unit_test_failed": 0,
  "unit_test_total": 15,
  "unit_test_points": 20,
  
  "functional_status": "pass",
  "functional_message": "Business outcome achieved",
  "functional_details": {...},
  "functional_points": 50,
  
  "bulk_status": "pass",
  "bulk_message": "Handled 200 records",
  "bulk_records_processed": 200,
  "bulk_records_expected": 200,
  "bulk_points": 10,
  
  "no_tweaks_status": "pass",
  "no_tweaks_message": "No manual tweaks needed",
  "no_tweaks_points": 10,
  
  "total_score": 100
}
```

### Component Status Values

- `"pass"`: Component validation passed
- `"fail"`: Component validation failed
- `"error"`: Error during component validation
- `"skipped"`: Component validation skipped

### Scoring

| Component | Max Points | Criteria |
|-----------|:----------:|----------|
| Deployment | 10 | Code deploys without errors |
| Unit Tests | 20 | All tests pass, coverage ≥80% |
| Functional | 50 | Business outcome achieved |
| Bulk | 10 | Handles 200+ records |
| No Tweaks | 10 | Works without manual fixes |
| **Total** | **100** | |

---

## Summary Object

Overall statistics for the evaluation.

```json
{
  "total_instances": 12,
  "resolved_instances": 5,
  "failed_instances": 2,
  "error_instances": 5,
  
  "resolve_rate": 41.67,
  
  "avg_score": 6.0,
  "median_score": 0.0,
  "min_score": 0,
  "max_score": 100,
  
  "deployment_pass_rate": 41.67,
  "unit_test_pass_rate": 33.33,
  "functional_pass_rate": 8.33,
  "bulk_pass_rate": 0.0,
  "no_tweaks_pass_rate": 41.67,
  
  "avg_duration_seconds": 245.3,
  "total_duration_seconds": 2943.6
}
```

---

## Example: Complete Report

```json
{
  "schema_version": "2.0",
  "run_id": "claude-sonnet-4.5-20251229",
  "model_name": "anthropic/claude-3.5-sonnet",
  "dataset": "verified",
  "config": {
    "tasks_file": "data/tasks/verified.json",
    "validation_mode": "functional",
    "max_workers": 2,
    "functional_validation": true
  },
  "instances": [
    {
      "instance_id": "lwc-component-001",
      "model_name": "anthropic/claude-3.5-sonnet",
      "status": "resolved",
      "resolved": true,
      "validation": {
        "deployment_status": "pass",
        "deployment_points": 10,
        "unit_test_status": "pass",
        "unit_test_points": 20,
        "functional_status": "pass",
        "functional_points": 50,
        "bulk_status": "pass",
        "bulk_points": 10,
        "no_tweaks_status": "pass",
        "no_tweaks_points": 10,
        "total_score": 100
      },
      "duration_seconds": 245.3
    }
  ],
  "summary": {
    "total_instances": 12,
    "resolved_instances": 5,
    "resolve_rate": 41.67,
    "avg_score": 6.0
  },
  "start_time": "2025-12-29T14:30:00Z",
  "end_time": "2025-12-29T16:45:00Z"
}
```

---

## Migration from v1

If you have v1 format results, use the migration function:

```python
from sfbench.utils.schema import migrate_v1_to_v2

v1_data = {...}  # Your v1 format data
v2_data = migrate_v1_to_v2(v1_data)
```

---

## Validation

Validate a report conforms to schema:

```python
from sfbench.utils.schema import validate_schema

is_valid = validate_schema(report_data)
```

---

## Tools & Libraries

### Python

```python
from sfbench.utils.schema import EvaluationReport, InstanceResult
from sfbench.utils.reporting import make_run_report

# Load report
with open('report.json') as f:
    data = json.load(f)
    report = EvaluationReport(**data)

# Generate markdown
from sfbench.utils.reporting import generate_markdown_summary
md = generate_markdown_summary(report)
```

### Command Line

```bash
# Validate schema
python -c "from sfbench.utils.schema import validate_schema; import json; print(validate_schema(json.load(open('report.json'))))"

# Convert v1 to v2
python -c "from sfbench.utils.schema import migrate_v1_to_v2; import json; print(json.dumps(migrate_v1_to_v2(json.load(open('v1_results.json'))), indent=2))"
```

---

## Related Documentation

- [Evaluation Guide](guides/evaluation.md)
- [Troubleshooting](guides/troubleshooting.md)
- [FAQ](../faq.md)

---

*Last updated: December 2025*
