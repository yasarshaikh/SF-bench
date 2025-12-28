<p align="center">
  <img src="https://img.shields.io/badge/SF--Bench-Salesforce%20AI%20Benchmark-00A1E0?style=for-the-badge&logo=salesforce&logoColor=white" alt="SF-Bench"/>
</p>

<h1 align="center">SF-Bench</h1>

<p align="center">
  <strong>The Industry's First Comprehensive Benchmark for Evaluating AI Coding Agents on Salesforce Development</strong>
</p>

<p align="center">
  <em>Real execution. Functional validation. Honest results.</em>
</p>

<p align="center">
  <a href="https://github.com/yasarshaikh/SF-bench/stargazers"><img src="https://img.shields.io/github/stars/yasarshaikh/SF-bench?style=social" alt="GitHub stars"/></a>
  <a href="https://github.com/yasarshaikh/SF-bench/network/members"><img src="https://img.shields.io/github/forks/yasarshaikh/SF-bench?style=social" alt="GitHub forks"/></a>
  <a href="https://github.com/yasarshaikh/SF-bench/issues"><img src="https://img.shields.io/github/issues/yasarshaikh/SF-bench" alt="GitHub issues"/></a>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"/></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"/></a>
  <a href="https://developer.salesforce.com/tools/salesforcecli"><img src="https://img.shields.io/badge/Salesforce-CLI%20v2+-00A1E0.svg?logo=salesforce" alt="Salesforce CLI"/></a>
  <a href="https://yasarshaikh.github.io/SF-bench/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-blue" alt="Documentation"/></a>
</p>

<p align="center">
  <a href="#-why-sf-bench">Why SF-Bench</a> •
  <a href="#-realistic-validation">Validation</a> •
  <a href="#-leaderboard">Leaderboard</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## 🎯 Why SF-Bench?

**The Salesforce ecosystem is a $50B+ market with millions of developers.** Yet there's no standardized way to evaluate how well AI coding assistants perform on Salesforce-specific tasks.

Generic benchmarks like **HumanEval** and **SWE-bench** don't capture:

| Challenge | Why It Matters |
|-----------|----------------|
| **Multi-modal development** | Apex, JavaScript (LWC), XML metadata, Flows |
| **Org-dependent testing** | Scratch orgs, governor limits, test frameworks |
| **Platform constraints** | Security model, sharing rules, field-level security |
| **Declarative vs. Code** | Flows, Process Builder, validation rules |
| **Enterprise patterns** | Triggers, batch jobs, integrations |

**SF-Bench fills this gap** with real execution in actual Salesforce environments.

---

## 🔬 Realistic Validation

> **"If a benchmark says 100% pass rate, it must mean the solution works 100% of the time in production, first try."**

### Most AI Benchmarks Are Broken

They check if code **compiles**, not if it **works**.

```
❌ Old Way:   Flow deployed successfully → PASS
✅ SF-Bench:  Flow deployed + Task created + Contact updated + Bulk works → PASS
```

### Expected Real-World Success Rates

Based on production Salesforce development experience:

| Task Type | Expected AI Success (One-Shot) | Notes |
|-----------|:------------------------------:|-------|
| **Apex Trigger** | 70-80% | Usually works, may need null checks |
| **LWC Component** | 60-70% | Error handling often incomplete |
| **Flow (Simple)** | 40-50% | Entry conditions often wrong |
| **Flow (Complex)** | 10-20% | Subflows, bulkification = nightmare |
| **Lightning Page** | 20-30% | Visibility rules complex |
| **Experience Cloud** | 10-20% | Guest access, security = hard |

**If an AI scores 100% on complex Flows, either the tasks are too easy or the validation is broken.**

### Validation Levels

| Level | Points | What We Check |
|-------|:------:|---------------|
| Syntax | 10 | Code parses, valid XML/JSON |
| Deployment | 20 | Deploys to scratch org |
| Unit Tests | 20 | All tests pass, coverage ≥80% |
| **Functional** | **40** | **Solution actually WORKS** |
| Production-Ready | 10 | Handles 200+ records, no governor limits |

---

## 🏆 Leaderboard

### Overall Results (December 2024)

| Rank | Model | Overall | Apex | LWC | Flow | Lightning Pages | Experience Cloud | Architecture |
|:----:|-------|:-------:|:----:|:---:|:----:|:---------------:|:----------------:|:------------:|
| 🥇 | **Gemini 3 Flash** | **75.0%** | 100% | 100% | 50% | 0% | 100% | 100% |
| 🥈 | **Gemini 2.5 Flash** | **75.0%** | 100% | 100% | 100% | 0% | 100% | 50% |
| 🥉 | *Submit results* | -% | -% | -% | -% | -% | -% | -% |

### Segment Breakdown

| Segment | Tasks | Gemini 3 Flash | Gemini 2.5 Flash |
|---------|:-----:|:--------------:|:----------------:|
| **Apex** | 2 | ✅ 2/2 (100%) | ✅ 2/2 (100%) |
| **LWC** | 2 | ✅ 2/2 (100%) | ✅ 2/2 (100%) |
| **Flow** | 2 | ⚠️ 1/2 (50%) | ✅ 2/2 (100%) |
| **Lightning Pages** | 1 | ❌ 0/1 (0%) | ❌ 0/1 (0%) |
| **Page Layouts** | 1 | ❌ 0/1 (0%) | ❌ 0/1 (0%) |
| **Experience Cloud** | 1 | ✅ 1/1 (100%) | ✅ 1/1 (100%) |
| **Architecture** | 2 | ✅ 2/2 (100%) | ⚠️ 1/2 (50%) |

**[📊 Submit your results →](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)**

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .
```

### Prerequisites

- **Python 3.10+**
- **[Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli)** (`sf` command)
- **Node.js 18+** (for LWC tasks)
- **Git**
- **Authenticated Dev Hub** (for Apex/Deploy tasks)

### Run Evaluation

```bash
# Quick evaluation (deployment validation only)
python scripts/evaluate.py --model <model-name> --tasks data/tasks/verified.json

# Realistic evaluation (functional validation - requires scratch org)
python scripts/evaluate.py --model <model-name> --tasks data/tasks/realistic.json \
    --functional --scratch-org <your-scratch-org>

# With pre-generated solutions
python scripts/evaluate.py --model gpt-4 --solutions solutions/gpt-4/
```

### Generate Leaderboard

```bash
python scripts/leaderboard.py --results-dir results/
```

---

## 📊 Task Types

SF-Bench covers **multiple task types** across the Salesforce ecosystem:

| Type | Description | Validation | Verified Repo |
|------|-------------|------------|:-------------:|
| `APEX` | Triggers, Classes, Integration | Apex unit tests + functional | apex-recipes |
| `LWC` | Lightning Web Components | Jest tests + deployment | lwc-recipes |
| `FLOW` | Record-Triggered, Screen Components | Deploy + outcome verification | automation-components |
| `LIGHTNING_PAGE` | FlexiPages, Dynamic Forms | Deploy + visibility rules | dreamhouse-lwc |
| `COMMUNITY` | Experience Cloud sites | Deploy + guest access test | ebikes-lwc |
| `ARCHITECTURE` | Full-stack, System Design | Multi-component validation | dreamhouse-lwc |

### Verified Repositories (API Confirmed)

| Repository | Stars | Description |
|------------|:-----:|-------------|
| [apex-recipes](https://github.com/trailheadapps/apex-recipes) | 1,059 ⭐ | Apex code examples |
| [lwc-recipes](https://github.com/trailheadapps/lwc-recipes) | 2,805 ⭐ | LWC examples |
| [dreamhouse-lwc](https://github.com/trailheadapps/dreamhouse-lwc) | 469 ⭐ | Real estate app |
| [automation-components](https://github.com/trailheadapps/automation-components) | 384 ⭐ | Flow actions |
| [ebikes-lwc](https://github.com/trailheadapps/ebikes-lwc) | 830 ⭐ | Experience Cloud |

---

## 📁 Project Structure

```
sf-bench/
├── sfbench/                  # Core evaluation framework
│   ├── engine.py             # Orchestration engine
│   ├── runners/              # Task-specific runners
│   │   ├── apex_runner.py
│   │   ├── lwc_runner.py
│   │   ├── flow_runner.py
│   │   └── architecture_runner.py
│   ├── validators/           # Functional validation
│   │   └── functional_validator.py
│   └── utils/                # Utilities
├── data/
│   ├── tasks/                # Task definitions
│   │   ├── verified.json     # Verified benchmark (12 tasks)
│   │   └── realistic.json    # Functional validation tasks
│   └── test-scripts/         # Apex test scripts
├── scripts/
│   ├── evaluate.py           # Run evaluations
│   └── leaderboard.py        # Generate leaderboard
├── docs/                     # Documentation site
└── examples/                 # Example solutions
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Submit Your Results
Run SF-Bench on your model and [submit results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) to be added to the leaderboard.

### Add New Tasks
Contribute real-world Salesforce tasks. See [CONTRIBUTING.md](CONTRIBUTING.md).

### Improve the Framework
Bug fixes, new runners, documentation improvements are all welcome!

---

## 📖 Citation

If you use SF-Bench in your research, please cite:

```bibtex
@software{sfbench2024,
  author = {Shaikh, Yasar},
  title = {SF-Bench: Benchmark for Evaluating AI Coding Agents on Salesforce Development},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yasarshaikh/SF-bench}
}
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Documentation**: [yasarshaikh.github.io/SF-bench](https://yasarshaikh.github.io/SF-bench/)
- **Issues**: [Report bugs or request features](https://github.com/yasarshaikh/SF-bench/issues)
- **Discussions**: [Join the community](https://github.com/yasarshaikh/SF-bench/discussions)

---

<p align="center">
  <strong>⭐ Star us on GitHub if you find SF-Bench useful!</strong>
</p>

<p align="center">
  Made with ❤️ for the Salesforce & AI community
</p>
