<p align="center">
  <img src="https://img.shields.io/badge/SF--Bench-Salesforce%20AI%20Benchmark-00A1E0?style=for-the-badge&logo=salesforce&logoColor=white" alt="SF-Bench"/>
</p>

<h1 align="center">SF-Bench</h1>

<p align="center">
  <strong>The First Comprehensive Benchmark for Evaluating AI Coding Agents on Salesforce Development</strong>
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
  <a href="#-leaderboard">Leaderboard</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-task-types">Tasks</a> •
  <a href="#-contributing">Contributing</a> •
  <a href="#-citation">Citation</a>
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

## 🏆 Leaderboard

### Overall Results (December 2024)

| Rank | Model | Overall | Apex | LWC | Flow | Lightning Pages | Experience Cloud | Architecture |
|:----:|-------|:-------:|:----:|:---:|:----:|:---------------:|:----------------:|:------------:|
| 🥇 | **Gemini 2.5 Flash** | **75.0%** | 100% | 100% | 100% | 0% | 100% | 50% |
| 🥈 | *Submit results* | -% | -% | -% | -% | -% | -% | -% |
| 🥉 | - | - | - | - | - | - | - | - |

### Segment Breakdown

| Segment | Tasks | Gemini 2.5 Flash | Notes |
|---------|:-----:|:----------------:|-------|
| **Apex** | 2 | ✅ 2/2 (100%) | Trigger handlers, integrations |
| **LWC** | 2 | ✅ 2/2 (100%) | Jest tests: 122/122 passed |
| **Flow** | 2 | ✅ 2/2 (100%) | Screen components, invocable actions |
| **Lightning Pages** | 1 | ❌ 0/1 (0%) | Dynamic forms - needs improvement |
| **Page Layouts** | 1 | ❌ 0/1 (0%) | Layout XML generation |
| **Experience Cloud** | 1 | ✅ 1/1 (100%) | Site customization |
| **Architecture** | 2 | ⚠️ 1/2 (50%) | Full-stack design |
| **Deployment** | 1 | ✅ 1/1 (100%) | Metadata validation |

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
# Evaluate your model
python scripts/evaluate.py --model <model-name> --solutions solutions/<model-name>/

# Example with GPT-4
python scripts/evaluate.py --model gpt-4 --solutions solutions/gpt-4/ --tasks data/tasks/full.json
```

### Generate Leaderboard

```bash
python scripts/leaderboard.py --results-dir results/
```

---

## 📊 Task Types

SF-Bench covers **12 verified task types** across the Salesforce ecosystem:

| Type | Description | Validation | Verified Repo |
|------|-------------|------------|:-------------:|
| `APEX` | Triggers, Classes, Integration | Apex unit tests | ✅ apex-recipes |
| `LWC` | Lightning Web Components | Jest tests | ✅ lwc-recipes |
| `FLOW` | Screen Components, Invocable Actions | Deploy + Tests | ✅ automation-components |
| `DEPLOY` | Metadata deployment | Deploy check | ✅ ebikes-lwc |
| `LIGHTNING_PAGE` | FlexiPages, Dynamic Forms | Deploy check | ✅ dreamhouse-lwc |
| `PAGE_LAYOUT` | Record Layouts | Deploy check | ✅ dreamhouse-lwc |
| `COMMUNITY` | Experience Cloud sites | Deploy check | ✅ ebikes-lwc |
| `ARCHITECTURE` | Full-stack, System Design | Multi-check | ✅ dreamhouse-lwc |
| `AGENTFORCE` | Agent Scripts, Prompts | Deploy check | ✅ agent-script-recipes |

### Verified Repositories (API Confirmed)

All tasks use **official Salesforce sample repositories** verified via GitHub API:

| Repository | Stars | Description |
|------------|:-----:|-------------|
| [apex-recipes](https://github.com/trailheadapps/apex-recipes) | 1,059 ⭐ | Apex code examples for common use cases |
| [lwc-recipes](https://github.com/trailheadapps/lwc-recipes) | 2,805 ⭐ | Lightning Web Components examples |
| [dreamhouse-lwc](https://github.com/trailheadapps/dreamhouse-lwc) | 469 ⭐ | Real estate sample app |
| [automation-components](https://github.com/trailheadapps/automation-components) | 384 ⭐ | Flow actions and screen components |
| [ebikes-lwc](https://github.com/trailheadapps/ebikes-lwc) | 830 ⭐ | Experience Cloud sample app |
| [agent-script-recipes](https://github.com/trailheadapps/agent-script-recipes) | 53 ⭐ | Agentforce script examples |
| [coral-cloud](https://github.com/trailheadapps/coral-cloud) | 138 ⭐ | Data Cloud and AI Prompts |

---

## 📈 Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     SF-BENCH EVALUATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LOAD TASKS          → Read from data/tasks/*.json            │
│  2. LOAD SOLUTIONS      → Load patches from solutions/<model>/   │
│  3. FOR EACH TASK:                                               │
│     ├── Clone repository at specified commit                     │
│     ├── Create scratch org (if needed)                           │
│     ├── Apply AI-generated solution patch                        │
│     ├── Deploy metadata                                          │
│     ├── Run validation (tests, deployment)                       │
│     ├── Record: PASS / FAIL / TIMEOUT / ERROR                    │
│     └── Cleanup (delete org, workspace)                          │
│  4. GENERATE RESULTS    → results/<model>/evaluation.json        │
│  5. UPDATE LEADERBOARD  → Rank by pass rate                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

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
│   └── utils/                # Utilities
├── data/
│   └── tasks/                # Task definitions
│       ├── dev.json          # Development set (3 tasks)
│       ├── verified.json     # Full verified benchmark (12 tasks)
│       └── full.json         # Full benchmark (12 tasks)
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
Run SF-Bench on your model and [submit results](https://github.com/yasarshaikh/SF-bench/issues/new) to be added to the leaderboard.

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
