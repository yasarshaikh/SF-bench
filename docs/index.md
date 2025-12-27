---
layout: default
title: SF-Bench
description: The first comprehensive benchmark for evaluating AI coding agents on Salesforce development tasks
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

| Feature | Description |
|---------|-------------|
| 🔄 **Real Execution** | Tests run in actual Salesforce scratch orgs |
| 📊 **15+ Task Types** | Apex, LWC, Flows, Lightning Pages, and more |
| 🏗️ **Architecture-Level** | Evaluates planning and system design |
| ✔️ **Outcome Validation** | Goes beyond just test passing |
| 📈 **Public Leaderboard** | Compare AI models head-to-head |

---

## 🏆 Leaderboard

| Rank | Model | Pass Rate | Tasks Passed | Date |
|:----:|-------|:---------:|:------------:|:----:|
| 🥇 | *Submit your results* | -% | -/- | - |
| 🥈 | - | - | - | - |
| 🥉 | - | - | - | - |

[**📊 Submit Your Results →**](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)

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

**Prerequisites:** Python 3.10+ • [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) • Node.js 18+ • Authenticated Dev Hub

---

## 📊 Task Coverage

| Category | Task Types | Validation |
|----------|------------|------------|
| **Development** | Apex, LWC, Triggers, Batch Jobs | Unit tests, Jest |
| **Declarative** | Flows, Validation Rules, Formulas | Flow validation |
| **Configuration** | Page Layouts, Lightning Pages, Communities | Deploy check |
| **Architecture** | Data Model, Security, Integration | Multi-layer validation |

---

## 🤝 Get Involved

| Action | Link |
|--------|------|
| ⭐ Star the repo | [GitHub Repository](https://github.com/yasarshaikh/SF-bench) |
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

**⭐ Star us on GitHub if you find SF-Bench useful!**

Made with ❤️ for the Salesforce & AI community
