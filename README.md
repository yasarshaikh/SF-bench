# SF-Bench

**Benchmark for evaluating AI coding agents on Salesforce development tasks.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

SF-Bench is a comprehensive benchmark for evaluating how well AI models can solve real-world Salesforce development tasks. Unlike generic coding benchmarks, SF-Bench tests domain-specific capabilities:

- **Apex**: Classes, triggers, and unit tests
- **LWC**: Lightning Web Components with Jest
- **Flows**: Salesforce Flow automation
- **Metadata**: Deployment and configuration
- **Architecture**: Planning and execution

## Quick Start

### Installation

```bash
git clone https://github.com/sfbench/sf-bench.git
cd sf-bench
pip install -e .
```

### Prerequisites

- Python 3.10+
- [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli) (`sf`)
- Node.js 18+ (for LWC tasks)
- Git
- Authenticated Dev Hub (for Apex/Deploy tasks)

### Run Evaluation

```bash
# Evaluate your model
python scripts/evaluate.py --model <your-model> --tasks data/tasks/dev.json

# With solutions
python scripts/evaluate.py --model gpt-4 --solutions solutions/gpt-4/
```

### View Results

```bash
# Generate leaderboard
python scripts/leaderboard.py --results-dir results/
```

---

## Evaluation Process

### A. How to Begin

1. **Prepare your model**: Ensure your AI model can generate Salesforce code
2. **Generate solutions**: For each task, generate a solution (as a git diff/patch)
3. **Save solutions**: Save as `.patch` files in `solutions/<model>/`

### B. The Process

```
┌─────────────────────────────────────────────────────────────┐
│                    EVALUATION PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. LOAD TASKS                                               │
│     └── Read task definitions from data/tasks/*.json         │
│                                                              │
│  2. LOAD SOLUTIONS                                           │
│     └── Load model solutions from solutions/<model>/         │
│                                                              │
│  3. FOR EACH TASK:                                           │
│     ├── Clone repository                                     │
│     ├── Checkout base commit                                 │
│     ├── Create scratch org (if needed)                       │
│     ├── Apply solution patch                                 │
│     ├── Deploy metadata                                      │
│     ├── Run validation (tests, deployment check)             │
│     ├── Record result (PASS/FAIL/TIMEOUT/ERROR)              │
│     └── Cleanup (delete org, remove workspace)               │
│                                                              │
│  4. GENERATE RESULTS                                         │
│     ├── Individual task results → results/<model>/*.json     │
│     ├── Evaluation summary → results/<model>/evaluation.json │
│     └── Leaderboard → leaderboard.json                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### C. Results Structure

#### Individual Task Result
```json
{
  "task_id": "sf-apex-001",
  "status": "PASS",
  "duration": 45.23,
  "timestamp": "2024-01-15T10:30:00",
  "details": {
    "tests_run": 5,
    "passed": 5,
    "failed": 0
  }
}
```

#### Evaluation Summary
```json
{
  "model": "gpt-4",
  "timestamp": "2024-01-15T10:30:00",
  "total_tasks": 50,
  "passed": 38,
  "failed": 8,
  "timeout": 2,
  "error": 2,
  "pass_rate": 76.0
}
```

#### Leaderboard
```json
{
  "entries": [
    {"rank": 1, "model": "claude-3-opus", "pass_rate": 82.0},
    {"rank": 2, "model": "gpt-4", "pass_rate": 76.0},
    {"rank": 3, "model": "gemini-pro", "pass_rate": 68.0}
  ]
}
```

---

## Task Types

| Type | Description | Validation |
|------|-------------|------------|
| `APEX` | Apex classes, triggers | Apex tests |
| `LWC` | Lightning Web Components | Jest tests |
| `FLOW` | Flow automation | Flow validation |
| `DEPLOY` | Metadata deployment | Deployment check |
| `ARCHITECTURE` | System design | Multi-check |

See `data/tasks/` for task definitions.

---

## Leaderboard

| Rank | Model | Pass Rate | Tasks |
|------|-------|-----------|-------|
| - | *Your model here* | - | - |

Submit your results to be added to the leaderboard!

---

## Project Structure

```
sf-bench/
├── sfbench/              # Main package
│   ├── engine.py         # Orchestrator
│   ├── runners/          # Task runners
│   └── utils/            # Utilities
├── data/
│   └── tasks/            # Task definitions
├── scripts/
│   ├── evaluate.py       # Run evaluation
│   └── leaderboard.py    # Generate leaderboard
├── docs/                 # Documentation
├── examples/             # Example solutions
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── pyproject.toml
```

---

## Contributing

We welcome contributions!

- **Submit results**: Run your model and submit via PR
- **Add tasks**: Contribute new Salesforce tasks
- **Improve code**: Bug fixes and features
- **Documentation**: Examples and guides

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## Citation

If you use SF-Bench in your research, please cite:

```bibtex
@software{sfbench2024,
  title = {SF-Bench: Benchmark for Salesforce AI Coding Agents},
  year = {2024},
  url = {https://github.com/sfbench/sf-bench}
}
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
