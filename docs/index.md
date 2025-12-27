---
layout: default
title: SF-Bench - Salesforce AI Benchmark
description: The first comprehensive benchmark for evaluating AI coding agents on Salesforce development tasks
---

<p align="center">
  <img src="https://img.shields.io/badge/SF--Bench-Salesforce%20AI%20Benchmark-00A1E0?style=for-the-badge&logo=salesforce&logoColor=white" alt="SF-Bench"/>
</p>

# SF-Bench

**The First Comprehensive Benchmark for Evaluating AI Coding Agents on Salesforce Development**

[![GitHub stars](https://img.shields.io/github/stars/yasarshaikh/SF-bench?style=social)](https://github.com/yasarshaikh/SF-bench)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/yasarshaikh/SF-bench/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Why SF-Bench?

The **Salesforce ecosystem represents $50B+ in annual revenue** with millions of developers worldwide. As AI coding assistants become mainstream, there's **no standardized benchmark** to evaluate their effectiveness on Salesforce-specific tasks.

**Generic benchmarks don't work for Salesforce:**

- ❌ HumanEval, SWE-bench don't test Apex, LWC, Flows
- ❌ No scratch org execution
- ❌ No platform-specific constraints
- ❌ No enterprise architecture patterns

**SF-Bench fills this gap** with:

- ✅ **Real execution** in Salesforce scratch orgs
- ✅ **15+ task types** covering all major clouds
- ✅ **Architecture-level** evaluation
- ✅ **Outcome validation** beyond just test passing

---

## 🏆 Leaderboard

| Rank | Model | Pass Rate |
|:----:|-------|:---------:|
| 🥇 | *Submit your results* | - |
| 🥈 | - | - |
| 🥉 | - | - |

[**Submit Results →**](https://github.com/yasarshaikh/SF-bench/issues/new)

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .

# Run evaluation
python scripts/evaluate.py --model your-model --solutions solutions/your-model/
```

---

## Task Coverage

| Category | Task Types |
|----------|------------|
| **Development** | Apex, LWC, Triggers, Batch Jobs |
| **Declarative** | Flows, Validation Rules, Formulas |
| **Configuration** | Page Layouts, Lightning Pages, Communities |
| **Architecture** | Data Model, Security, Integration |

---

## Links

- [**GitHub Repository**](https://github.com/yasarshaikh/SF-bench)
- [**Documentation**](https://github.com/yasarshaikh/SF-bench#readme)
- [**Contributing Guide**](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md)
- [**Submit Results**](https://github.com/yasarshaikh/SF-bench/issues/new)

---

<p align="center">
  <strong>⭐ Star us on GitHub!</strong><br>
  <a href="https://github.com/yasarshaikh/SF-bench">github.com/yasarshaikh/SF-bench</a>
</p>
