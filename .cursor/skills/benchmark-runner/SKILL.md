---
name: benchmark-runner
description: Guides evaluation workflow execution for SF-Bench. The agent invokes this skill when running evaluations, discussing scoring methodology, or working with the evaluation pipeline.
---

# Benchmark Runner

## Overview

This skill provides expertise in executing SF-Bench evaluations, understanding the scoring methodology, and managing the evaluation pipeline.

## When This Skill Applies

- Running or discussing evaluation workflows
- Questions about scoring or metrics
- Working with evaluation scripts
- Managing checkpoints and results
- Understanding task execution flow

## Evaluation Pipeline

### Pipeline Stages

```
1. Preflight Checks
   ├── API Key validation
   ├── DevHub connectivity
   ├── Scratch org capacity
   └── LLM model validation

2. Solution Generation
   ├── Load task definition
   ├── Generate prompt from task
   ├── Call AI provider API
   └── Validate git diff format

3. Task Execution
   ├── Clone task repository
   ├── Apply solution patch
   ├── Create scratch org
   ├── Deploy to scratch org
   └── Execute validation

4. Validation
   ├── Deployment validation (code compiles/deploys)
   ├── Test validation (unit tests pass)
   └── Functional validation (business outcome achieved)

5. Scoring & Reporting
   ├── Calculate component scores
   ├── Aggregate results
   ├── Generate reports (JSON + Markdown)
   └── Create checkpoint
```

### Running Evaluations

#### Basic Evaluation
```bash
python scripts/evaluate.py \
    --model grok-4.1-fast \
    --tasks data/tasks/verified.json
```

#### With Functional Validation
```bash
python scripts/evaluate.py \
    --model claude-3-opus \
    --tasks data/tasks/realistic.json \
    --functional
```

#### Resume from Checkpoint
```bash
python scripts/evaluate.py \
    --model gemini-pro \
    --tasks data/tasks/verified.json \
    --output results/existing-run-dir/
```

#### With Pre-Generated Solutions
```bash
python scripts/evaluate.py \
    --model gpt-4 \
    --tasks data/tasks/verified.json \
    --solutions solutions/gpt-4/
```

## Scoring Methodology

### Component Weights

| Component | Weight | Description |
|-----------|--------|-------------|
| Deployment | 10% | Code deploys without errors |
| Tests | 20% | Unit tests pass |
| Functional | 50% | Business outcome achieved |
| Bulk | 10% | Handles 200+ records |
| No Tweaks | 10% | No manual modifications needed |

### Score Calculation
```python
score = (
    deploy_score * 0.10 +
    test_score * 0.20 +
    functional_score * 0.50 +
    bulk_score * 0.10 +
    no_tweaks_score * 0.10
)
```

### Pass/Fail Criteria

- **Pass**: Score ≥ 0.6 (60%)
- **Fail**: Score < 0.6
- **Partial**: Some components pass, others fail

## Task Types

### Apex Tasks
- Trigger implementation
- Class development
- Test class creation
- Bulk operation handling

### LWC Tasks
- Component creation
- Apex controller integration
- Event handling
- Wire service usage

### Flow Tasks
- Record-triggered flows
- Screen flows
- Scheduled flows
- Flow variables and formulas

### Architecture Tasks
- Cross-cutting concerns
- Integration patterns
- Multi-object solutions

## Checkpoint Management

### Checkpoint Structure
```json
{
    "evaluation_id": "run-20260127-123456",
    "completed_tasks": ["task-001", "task-002"],
    "results": {...},
    "metadata": {
        "model": "grok-4.1-fast",
        "provider": "routellm",
        "timestamp": "2026-01-27T12:34:56Z"
    },
    "hash": "sha256:abc123..."
}
```

### Resume Behavior
1. Load checkpoint from output directory
2. Verify checkpoint integrity (hash)
3. Skip completed tasks
4. Continue from next pending task
5. Merge results on completion

## Result Schema (v2)

### SWE-bench Compatible Format
```json
{
    "model_name_or_path": "grok-4.1-fast",
    "instance_id": "task-001",
    "model_patch": "--- a/file.cls\n+++ b/file.cls\n...",
    "resolved": true,
    "scores": {
        "deploy": 1.0,
        "tests": 1.0,
        "functional": 1.0,
        "bulk": 1.0,
        "no_tweaks": 1.0,
        "total": 1.0
    }
}
```

## Troubleshooting Evaluations

### Common Issues

#### Preflight Failure
- Check API key environment variables
- Verify DevHub authentication: `sf org list --all`
- Check scratch org limits

#### Solution Generation Failure
- Verify model is available via provider
- Check API key permissions
- Review rate limit status

#### Deployment Failure
- Check patch format (valid git diff)
- Review Salesforce error messages
- Verify scratch org is active

#### Validation Failure
- Check test assertions
- Review functional validation script
- Verify test data setup

### Debug Commands
```bash
# Check DevHub orgs
sf org list --all

# View scratch org details
sf org display -o <alias>

# Run tests manually
sf apex run test -o <alias> -n <TestClass> -r human

# Execute anonymous Apex
sf apex run -o <alias> -f test-script.apex
```
