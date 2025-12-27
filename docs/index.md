---
layout: default
title: SF-Bench
---

# SF-Bench

**Benchmark for evaluating AI coding agents on Salesforce development tasks.**

---

## What is SF-Bench?

SF-Bench is a comprehensive benchmark for evaluating how well AI models can solve real-world Salesforce development tasks. It tests domain-specific capabilities across:

- **Apex**: Classes, triggers, and unit tests
- **LWC**: Lightning Web Components with Jest
- **Flows**: Salesforce Flow automation  
- **Metadata**: Deployment and configuration
- **Architecture**: Planning and execution

## Why SF-Bench?

Generic coding benchmarks (HumanEval, SWE-bench) don't capture Salesforce-specific challenges:

- Multi-modal development (Apex, JavaScript, XML)
- Org-dependent testing (scratch orgs, test frameworks)
- Platform constraints (governor limits, security model)
- Architecture patterns (flows, triggers, LWC)

SF-Bench fills this gap with real execution in actual Salesforce environments.

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/sfbench/sf-bench.git
cd sf-bench
pip install -e .

# Run evaluation
python scripts/evaluate.py --model gpt-4 --tasks data/tasks/dev.json
```

---

## Leaderboard

| Rank | Model | Pass Rate |
|------|-------|-----------|
| - | *Submit your results* | - |

[Submit Results →](https://github.com/sfbench/sf-bench/issues/new)

---

## Links

- [GitHub Repository](https://github.com/sfbench/sf-bench)
- [Documentation](https://sfbench.github.io/sf-bench)
- [Contributing Guide](https://github.com/sfbench/sf-bench/blob/main/CONTRIBUTING.md)
