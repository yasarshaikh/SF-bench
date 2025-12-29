---
layout: default
title: Benchmark Details - SF-Bench Technical Specifications
description: Detailed technical specifications and evaluation results for SF-Bench. Task categories, difficulty breakdown, and verified repositories used in the benchmark.
keywords: salesforce benchmark specifications, ai benchmark details, salesforce evaluation tasks, benchmark technical details
---

# SF-Bench Evaluation Results

## Leaderboard by Segment

| Segment | Description | GPT-4o | Claude 3.5 | Gemini 2.0 | Llama 3.3 |
|---------|-------------|:------:|:----------:|:----------:|:---------:|
| **Apex** | Triggers, Classes, Tests | -% | -% | -% | -% |
| **LWC** | Lightning Web Components | -% | -% | -% | -% |
| **Flow** | Screen Components, Invocable Actions | -% | -% | -% | -% |
| **Lightning Pages** | FlexiPages, Dynamic Forms | -% | -% | -% | -% |
| **Page Layouts** | Record Layouts, Compact Layouts | -% | -% | -% | -% |
| **Experience Cloud** | Sites, Communities | -% | -% | -% | -% |
| **Architecture** | Full-stack, System Design | -% | -% | -% | -% |
| **Deployment** | Metadata, Dependencies | -% | -% | -% | -% |
| **Agentforce** | Agent Scripts, Prompts | -% | -% | -% | -% |
| | | | | | |
| **Overall** | All Tasks | **-%** | **-%** | **-%** | **-%** |

---

## Task Difficulty Breakdown

| Difficulty | Total Tasks | Description |
|------------|:-----------:|-------------|
| Easy | 2 | Basic configurations, simple fixes |
| Medium | 5 | Multi-step implementations, integrations |
| Hard | 4 | Complex components, advanced patterns |
| Expert | 1 | Full architecture, multi-layer solutions |

---

## Verified Repositories Used

| Repository | Stars | Categories | Status |
|------------|:-----:|------------|:------:|
| [trailheadapps/apex-recipes](https://github.com/trailheadapps/apex-recipes) | 1,059 | Apex | ✅ Active |
| [trailheadapps/lwc-recipes](https://github.com/trailheadapps/lwc-recipes) | 2,805 | LWC | ✅ Active |
| [trailheadapps/dreamhouse-lwc](https://github.com/trailheadapps/dreamhouse-lwc) | 469 | LWC, Architecture | ✅ Active |
| [trailheadapps/automation-components](https://github.com/trailheadapps/automation-components) | 384 | Flow | ✅ Active |
| [trailheadapps/ebikes-lwc](https://github.com/trailheadapps/ebikes-lwc) | 830 | Experience Cloud | ✅ Active |
| [trailheadapps/agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) | 53 | Agentforce | ✅ Active |
| [trailheadapps/coral-cloud](https://github.com/trailheadapps/coral-cloud) | 138 | Data Cloud, AI | ✅ Active |

---

## Evaluation Methodology

### Validation Criteria

Each task is evaluated on multiple dimensions:

1. **Functional Correctness** (40%)
   - Tests pass
   - Deployment succeeds
   - Expected behavior achieved

2. **Code Quality** (30%)
   - No hardcoded values
   - Proper error handling
   - Follows Salesforce best practices

3. **Anti-Gaming Checks** (20%)
   - No test-specific hacks
   - Solution addresses root cause
   - Maintainable code

4. **Documentation** (10%)
   - Clear comments
   - README updates where applicable

### Scoring

- **Pass**: Score ≥ 80%
- **Partial**: 50% ≤ Score < 80%
- **Fail**: Score < 50%

---

## Submit Your Results

Run SF-Bench on your model and submit results:

```bash
python scripts/evaluate.py --model <your-model> --tasks data/tasks/verified.json
```

Then [submit your results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) to be added to the leaderboard.

---

*Last updated: December 2025*

