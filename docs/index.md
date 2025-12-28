---
layout: default
title: SF-Bench - Salesforce AI Benchmark
description: The industry's first comprehensive benchmark for evaluating AI coding agents on Salesforce development. Real execution, functional validation, honest results.
---

# SF-Bench: The Salesforce AI Coding Benchmark

**The industry's first comprehensive benchmark for evaluating AI coding agents on Salesforce development tasks.**

Unlike generic benchmarks (HumanEval, SWE-bench), SF-Bench tests what actually matters for Salesforce developers:

- ✅ **Real Execution**: Tests run in actual Salesforce scratch orgs
- ✅ **Functional Validation**: We verify the solution *works*, not just deploys
- ✅ **Platform Constraints**: Governor limits, security model, bulkification
- ✅ **Multi-Modal**: Apex, LWC (JavaScript), Flows (XML), Lightning Pages, Metadata

---

## 🏆 Leaderboard (December 2024)

| Segment | Gemini 3 Flash | Gemini 2.5 Flash | GPT-4o | Claude 3.5 |
|---------|:--------------:|:----------------:|:------:|:----------:|
| **Apex** | ✅ 100% | ✅ 100% | -% | -% |
| **LWC** | ✅ 100% | ✅ 100% | -% | -% |
| **Flow** | ⚠️ 50% | ✅ 100% | -% | -% |
| **Lightning Pages** | ❌ 0% | ❌ 0% | -% | -% |
| **Experience Cloud** | ✅ 100% | ✅ 100% | -% | -% |
| **Architecture** | ✅ 100% | ⚠️ 50% | -% | -% |
| | | | | |
| **Overall** | **75.0%** | **75.0%** | **-%** | **-%** |

**🏅 Both Gemini Flash models achieve 75% on SF-Bench!**

[**📊 Submit Your Results →**](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)

---

## 🔬 Realistic Validation

**Most AI benchmarks are broken.** They check if code compiles, not if it works.

SF-Bench validates **actual functionality**:

```
❌ Old Way: "Flow deployed" = PASS
✅ SF-Bench: "Flow deployed" + "Task created" + "Contact updated" + "Bulk works" = PASS
```

### Expected Real-World Success Rates

Based on production Salesforce development experience:

| Task Type | Expected AI Success | Notes |
|-----------|:-------------------:|-------|
| **Apex Trigger** | 70-80% | Usually works, may need tweaks |
| **LWC Component** | 60-70% | Error handling often incomplete |
| **Flow (Simple)** | 40-50% | Entry conditions often wrong |
| **Flow (Complex)** | 10-20% | Subflows, bulk = nightmare |
| **Lightning Page** | 20-30% | Visibility rules complex |
| **Experience Cloud** | 10-20% | Guest access, security hard |

**If an AI scores 100% on Flows, the benchmark is broken.**

---

## 📊 Task Categories

| Category | Description | Tasks |
|----------|-------------|:-----:|
| **Apex** | Triggers, Classes, Integration | 2 |
| **LWC** | Lightning Web Components | 2 |
| **Flow** | Screen Components, Record-Triggered | 2 |
| **Lightning Pages** | FlexiPages, Dynamic Forms | 1 |
| **Experience Cloud** | Guest Access, Sites | 1 |
| **Architecture** | Full-Stack Design | 2 |

### Verified Repositories

All tasks use **official Salesforce sample repositories**:

| Repository | Stars | Categories |
|------------|:-----:|------------|
| [apex-recipes](https://github.com/trailheadapps/apex-recipes) | 1,059 ⭐ | Apex |
| [lwc-recipes](https://github.com/trailheadapps/lwc-recipes) | 2,805 ⭐ | LWC |
| [dreamhouse-lwc](https://github.com/trailheadapps/dreamhouse-lwc) | 469 ⭐ | Architecture |
| [automation-components](https://github.com/trailheadapps/automation-components) | 384 ⭐ | Flow |
| [ebikes-lwc](https://github.com/trailheadapps/ebikes-lwc) | 830 ⭐ | Experience Cloud |

---

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .

# Run evaluation (deployment validation)
python scripts/evaluate.py --model <your-model> --tasks data/tasks/verified.json

# Run evaluation (full functional validation - requires scratch org)
python scripts/evaluate.py --model <your-model> --tasks data/tasks/realistic.json \
    --functional --scratch-org <your-scratch-org>
```

**Prerequisites:** Python 3.10+ • [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) • Node.js 18+ • Authenticated Dev Hub

---

## 🎯 Why SF-Bench?

| What Generic Benchmarks Miss | Why It Matters |
|------------------------------|----------------|
| ❌ No Apex/LWC testing | Salesforce's primary languages |
| ❌ No scratch org execution | Real platform validation |
| ❌ No governor limits | Critical platform constraints |
| ❌ No declarative tools | Flows, validation rules, formulas |
| ❌ No enterprise patterns | Triggers, batch jobs, integrations |

**The Salesforce ecosystem represents $50B+ in annual revenue** with millions of developers worldwide. SF-Bench provides the standardized evaluation the industry needs.

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

## Keywords

Salesforce AI Benchmark • AI Coding Agents • Apex Testing • LWC Testing • Flow Automation • Lightning Web Components • Salesforce Development • LLM Evaluation • AI Code Generation • Salesforce Developer Tools • Agentforce • Einstein AI • Copilot Salesforce • AI Benchmark 2024

---

**⭐ Star us on GitHub if you find SF-Bench useful!**

Made with ❤️ for the Salesforce & AI community
