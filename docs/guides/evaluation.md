---
layout: default
title: Evaluation Guide
description: Complete guide to running SF-Bench evaluations
---

# Evaluation Guide

Complete guide to running SF-Bench evaluations, from basic usage to advanced configurations.

---

## Quick Start

```bash
# Basic evaluation
python scripts/evaluate.py \
  --model "anthropic/claude-3.5-sonnet" \
  --tasks data/tasks/verified.json

# With functional validation
python scripts/evaluate.py \
  --model "anthropic/claude-3.5-sonnet" \
  --tasks data/tasks/verified.json \
  --functional
```

---

## Command-Line Options

### Required Arguments

- `--model`: Model name or identifier
  - Examples: `"anthropic/claude-3.5-sonnet"`, `"gemini-2.5-flash"`, `"gpt-4"`
  
- `--tasks`: Path to tasks JSON file
  - Examples: `data/tasks/verified.json`, `data/tasks/lite.json`

### Optional Arguments

- `--functional`: Enable functional validation (default: disabled)
  - Validates actual business outcomes, not just deployment
  - Adds 50% weight to functional tests
  
- `--max-workers`: Number of parallel workers (default: 3)
  - Higher = faster but more scratch orgs needed
  - Recommended: 2-4 for most setups
  
- `--output`: Output directory (default: `results/<model-name>`)
  - Custom path for results
  
- `--provider`: Explicitly specify AI provider
  - Options: `openrouter`, `routellm`, `gemini`, `anthropic`, `openai`, `ollama`
  - Auto-detected if not specified
  
- `--skip-devhub`: Skip DevHub connectivity check
  - Use if DevHub check fails but orgs still work
  
- `--skip-preflight`: Skip all pre-flight checks
  - Not recommended - may waste resources
  
- `--skip-llm-check`: Skip LLM format validation
  - Faster startup, but may fail later if format is wrong
  
- `--interactive`: Enable interactive prompts for missing config
  - Helpful for first-time setup

---

## Evaluation Modes

### 1. Deployment-Only Validation (Default)

**What it checks:**
- ✅ Code deploys successfully
- ✅ No syntax errors
- ✅ Metadata is valid

**Use when:**
- Quick smoke test
- Testing deployment pipeline
- Limited scratch org capacity

**Command:**
```bash
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/verified.json
```

**Time:** ~30-45 minutes for 12 tasks

---

### 2. Functional Validation (Recommended)

**What it checks:**
- ✅ Code deploys (10%)
- ✅ Unit tests pass (20%)
- ✅ **Business outcome achieved (50%)**
- ✅ Bulk operations work (10%)
- ✅ No manual tweaks needed (10%)

**Use when:**
- Realistic performance measurement
- Comparing models objectively
- Production readiness assessment

**Command:**
```bash
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/verified.json \
  --functional
```

**Time:** ~1-2 hours for 12 tasks

---

## Understanding Results

### Result Files

After evaluation, you'll find:

```
results/<model-name>/
├── report.json          # Schema v2 report (machine-readable)
├── summary.md           # Human-readable summary
├── evaluation_*.json    # Legacy format (backward compatibility)
└── <task-id>.json       # Individual task results
```

### Reading the Report

**Schema v2 Report (`report.json`):**
```json
{
  "schema_version": "2.0",
  "run_id": "claude-sonnet-4.5-20251229",
  "model_name": "anthropic/claude-3.5-sonnet",
  "summary": {
    "total_instances": 12,
    "resolved_instances": 5,
    "resolve_rate": 41.67,
    "avg_score": 6.0
  },
  "instances": [...]
}
```

**Markdown Summary (`summary.md`):**
- Overall results table
- Component breakdown
- Individual task details
- Performance metrics

---

## Scoring System

### Component Weights

| Component | Weight | What It Measures |
|-----------|:------:|------------------|
| **Deployment** | 10% | Code deploys without errors |
| **Unit Tests** | 20% | All tests pass, coverage ≥80% |
| **Functional** | 50% | Business outcome achieved |
| **Bulk Operations** | 10% | Handles 200+ records |
| **No Manual Tweaks** | 10% | Works in one shot |

**Total: 100 points**

### Success Criteria

A task is **RESOLVED** if:
- ✅ Deployment: PASS
- ✅ Unit Tests: PASS
- ✅ Functional: PASS
- ✅ Total Score ≥ 80/100

---

## Advanced Usage

### Using Pre-Generated Solutions

```bash
# Generate solutions first
python scripts/generate_solutions.py \
  --model "your-model" \
  --tasks data/tasks/verified.json \
  --output solutions/

# Then evaluate
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/verified.json \
  --solutions solutions/
```

### Parallel Evaluation

```bash
# Use 4 workers for faster evaluation
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/verified.json \
  --max-workers 4
```

**Note:** Each worker needs a scratch org. Ensure you have enough capacity.

### Custom Scratch Org

```bash
# Use existing scratch org
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/verified.json \
  --scratch-org-alias "my-existing-org"
```

---

## Performance Tips

### Faster Evaluations

1. **Use fewer workers** if scratch org creation is slow
2. **Skip LLM format check** if you've tested the model before
3. **Use deployment-only** mode for quick tests
4. **Pre-generate solutions** to avoid API rate limits

### Resource Management

1. **Monitor scratch org limits** before starting
2. **Clean up old orgs** regularly
3. **Use multiple DevHubs** for parallel runs
4. **Check API quotas** for your provider

---

## Troubleshooting

### Common Issues

**"All tasks failed with ERROR"**
- Check pre-flight checks output
- Verify DevHub authentication
- Check scratch org limits

**"Corrupt patch errors"**
- Some models generate invalid patches
- Try a different model or provider
- See [Troubleshooting Guide](troubleshooting.md) for details

**"Scratch org creation timeout"**
- Check network connectivity
- Verify DevHub limits
- Try with fewer workers

See [Troubleshooting Guide](troubleshooting.md) for more solutions.

---

## Best Practices

### 1. Always Use Pre-Flight Checks

```bash
# Pre-flight checks run automatically
# They catch issues before wasting resources
```

### 2. Start with Lite Dataset

```bash
# Test with 5 tasks first
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/lite.json
```

### 3. Use Functional Validation for Real Results

```bash
# Deployment-only can be misleading
# Functional validation shows real capability
--functional
```

### 4. Monitor Resources

```bash
# Check scratch org capacity
python -c "from sfbench.utils.inventory import ScratchOrgInventory; ScratchOrgInventory().print_inventory_report()"
```

---

## Next Steps

- 📖 [Understanding Results](reference/result-schema.md)
- 🔧 [Troubleshooting](troubleshooting.md)
- 📊 [Leaderboard](../LEADERBOARD.md)
- ❓ [FAQ](../faq.md)

---

*Last updated: December 2025*
