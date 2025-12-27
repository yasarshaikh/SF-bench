---
name: Submit Results
about: Submit your model's SF-Bench evaluation results
title: "[RESULTS] Model Name - Pass Rate%"
labels: results
assignees: ''
---

## Model Information

**Model Name:** 
**Provider:** (e.g., OpenAI, Anthropic, Google, Open Source)
**Model Version:** 

## Results

**Task Set:** (dev.json / full.json)
**Pass Rate:** X%
**Total Tasks:** 
**Passed:** 
**Failed:** 
**Timeout:** 
**Error:** 

## Evaluation Details

**Date:** 
**SF-Bench Version:** 
**Command Used:**
```bash
python scripts/evaluate.py --model <model> --tasks <tasks>
```

## Attach Results

Please attach or paste your `evaluation.json` file:

```json
{
  "model": "",
  "pass_rate": 0,
  "passed": 0,
  "total_tasks": 0
}
```

## Notes

Any additional context about the evaluation (prompting strategy, etc.)

