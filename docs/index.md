---
layout: default
title: Home
description: The first comprehensive benchmark for evaluating AI coding agents on Salesforce development tasks
---

<div align="center">
  
# 🔬 SF-Bench

### **The First Comprehensive Benchmark for Evaluating AI Coding Agents on Salesforce Development**

[![GitHub stars](https://img.shields.io/github/stars/yasarshaikh/SF-bench?style=for-the-badge)](https://github.com/yasarshaikh/SF-bench)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://github.com/yasarshaikh/SF-bench/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Salesforce](https://img.shields.io/badge/Salesforce-CLI%20v2+-00A1E0.svg?style=for-the-badge&logo=salesforce&logoColor=white)](https://developer.salesforce.com/)

</div>

---

## 🎯 The Problem

**The Salesforce ecosystem represents $50B+ in annual revenue** with millions of developers worldwide. As AI coding assistants become mainstream, there's **no standardized benchmark** to evaluate their effectiveness on Salesforce-specific tasks.

| What Generic Benchmarks Miss | Why It Matters |
|------------------------------|----------------|
| ❌ No Apex/LWC testing | Salesforce's primary languages |
| ❌ No scratch org execution | Real platform validation |
| ❌ No governor limits | Critical platform constraints |
| ❌ No declarative tools | Flows, validation rules, formulas |
| ❌ No enterprise patterns | Triggers, batch jobs, integrations |

---

## ✅ The Solution

**SF-Bench** fills this gap with:

- 🔄 **Real execution** in Salesforce scratch orgs
- 📊 **15+ task types** covering all major clouds
- 🏗️ **Architecture-level** evaluation
- ✔️ **Outcome validation** beyond just test passing
- 📈 **Public leaderboard** for model comparison

---

## 🏆 Leaderboard

| Rank | Model | Pass Rate | Tasks Passed | Date |
|:----:|-------|:---------:|:------------:|:----:|
| 🥇 | *Submit your results* | -% | -/- | - |
| 🥈 | - | - | - | - |
| 🥉 | - | - | - | - |

**[Submit Your Results →](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)**

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .

# Run evaluation
python scripts/evaluate.py --model <your-model> --solutions solutions/<your-model>/
```

**Prerequisites:** Python 3.10+, [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli), Node.js 18+, Authenticated Dev Hub

---

## 📊 Task Coverage

| Category | Task Types | Validation |
|----------|------------|------------|
| **Development** | Apex, LWC, Triggers, Batch Jobs | Unit tests, Jest |
| **Declarative** | Flows, Validation Rules, Formulas | Flow/formula validation |
| **Configuration** | Page Layouts, Lightning Pages, Communities | Deploy check |
| **Architecture** | Data Model, Security, Integration | Multi-layer validation |

---

## 📁 Project Structure

```
sf-bench/
├── sfbench/                  # Core evaluation framework
│   ├── engine.py             # Orchestration engine
│   └── runners/              # Task-specific runners
├── data/tasks/               # Task definitions
├── scripts/                  # Evaluation & leaderboard scripts
└── docs/                     # Documentation
```

---

## 🤝 Get Involved

| Action | Link |
|--------|------|
| ⭐ Star the repo | [github.com/yasarshaikh/SF-bench](https://github.com/yasarshaikh/SF-bench) |
| 📊 Submit results | [Submit Results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) |
| 🐛 Report bugs | [Issue Tracker](https://github.com/yasarshaikh/SF-bench/issues) |
| 💬 Discussions | [GitHub Discussions](https://github.com/yasarshaikh/SF-bench/discussions) |
| 📝 Contribute | [Contributing Guide](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md) |

---

## 📖 Citation

```bibtex
@software{sfbench2024,
  author = {Shaikh, Yasar},
  title = {SF-Bench: Benchmark for Evaluating AI Coding Agents on Salesforce Development},
  year = {2024},
  url = {https://github.com/yasarshaikh/SF-bench}
}
```

---

<div align="center">
  
**⭐ Star us on GitHub if you find SF-Bench useful!**

Made with ❤️ for the Salesforce & AI community

</div>
