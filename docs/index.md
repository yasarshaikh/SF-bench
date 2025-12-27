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

## 🏆 Leaderboard by Segment

| Segment | Description | GPT-4o | Claude 3.5 | Gemini 2.0 | Open Source |
|---------|-------------|:------:|:----------:|:----------:|:-----------:|
| **Apex** | Triggers, Classes, Tests | -% | -% | -% | -% |
| **LWC** | Lightning Web Components | -% | -% | -% | -% |
| **Flow** | Screen Components, Actions | -% | -% | -% | -% |
| **Lightning Pages** | FlexiPages, Dynamic Forms | -% | -% | -% | -% |
| **Experience Cloud** | Sites, Communities | -% | -% | -% | -% |
| **Architecture** | Full-stack, System Design | -% | -% | -% | -% |
| | | | | | |
| **Overall** | All 12 Tasks | **-%** | **-%** | **-%** | **-%** |

[**📊 Submit Your Results →**](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)

---

## ✅ Verified Repositories

All tasks use **official Salesforce sample repositories** verified via GitHub API:

| Repository | Stars | Categories |
|------------|:-----:|------------|
| [apex-recipes](https://github.com/trailheadapps/apex-recipes) | 1,059 ⭐ | Apex |
| [lwc-recipes](https://github.com/trailheadapps/lwc-recipes) | 2,805 ⭐ | LWC |
| [dreamhouse-lwc](https://github.com/trailheadapps/dreamhouse-lwc) | 469 ⭐ | Architecture |
| [automation-components](https://github.com/trailheadapps/automation-components) | 384 ⭐ | Flow |
| [ebikes-lwc](https://github.com/trailheadapps/ebikes-lwc) | 830 ⭐ | Experience Cloud |
| [agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) | 53 ⭐ | Agentforce |

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .

# Run evaluation
python scripts/evaluate.py --model <your-model> --tasks data/tasks/verified.json
```

**Prerequisites:** Python 3.10+ • [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) • Node.js 18+ • Authenticated Dev Hub

---

## 📊 Task Difficulty

| Difficulty | Tasks | Description |
|------------|:-----:|-------------|
| Easy | 2 | Basic configurations, simple fixes |
| Medium | 5 | Multi-step implementations |
| Hard | 4 | Complex components, patterns |
| Expert | 1 | Full architecture design |

---

## 🤝 Get Involved

| Action | Link |
|--------|------|
| ⭐ Star the repo | [GitHub Repository](https://github.com/yasarshaikh/SF-bench) |
| 📊 Submit results | [Submit Results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) |
| 🐛 Report bugs | [Issue Tracker](https://github.com/yasarshaikh/SF-bench/issues) |
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
