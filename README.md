<p align="center">
  <img src="https://img.shields.io/badge/SF--Bench-Salesforce%20AI%20Benchmark-00A1E0?style=for-the-badge&logo=salesforce&logoColor=white" alt="SF-Bench"/>
</p>

<h1 align="center">SF-Bench</h1>

<p align="center">
  <strong>The Open Benchmark for Evaluating AI Coding Agents on Salesforce Development</strong>
</p>

<p align="center">
  <a href="https://github.com/yasarshaikh/SF-bench/stargazers"><img src="https://img.shields.io/github/stars/yasarshaikh/SF-bench?style=social" alt="GitHub stars"/></a>
  <a href="https://github.com/yasarshaikh/SF-bench/network/members"><img src="https://img.shields.io/github/forks/yasarshaikh/SF-bench?style=social" alt="GitHub forks"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"/></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"/></a>
</p>

---

## 📌 Quick Navigation

| I want to... | Go to |
|--------------|-------|
| 🏆 **See benchmark results** | [Leaderboard](#-leaderboard) |
| 🧪 **Test my AI model** | [Testing Your Model](#-testing-your-model) |
| ➕ **Add new tasks** | [Contributing Tasks](#-contributing-tasks) |
| 🔧 **Understand the methodology** | [How It Works](#-how-it-works) |
| 🚀 **Get started quickly** | [Quick Start](#-quick-start) |

---

## 🎯 What is SF-Bench?

SF-Bench is an **open, objective benchmark** for measuring how well AI coding agents perform on Salesforce development tasks.

**We are auditors, not predictors.** We:
- ✅ Measure actual performance
- ✅ Report objective results  
- ✅ Verify functional outcomes
- ❌ ~~Don't predict what models "should" score~~
- ❌ ~~Don't claim expected success rates~~

### Why Salesforce-Specific?

Generic benchmarks (HumanEval, SWE-bench) miss Salesforce-specific challenges:

| Challenge | What We Test |
|-----------|--------------|
| Multi-modal development | Apex, LWC (JavaScript), Flows (XML), Metadata |
| Platform execution | Real scratch orgs, not just syntax checks |
| Governor limits | CPU time, SOQL queries, heap size |
| Declarative tools | Flows, Lightning Pages, Permission Sets |
| Enterprise patterns | Triggers, batch jobs, integrations |

---

## 🏆 Leaderboard

*Results as of December 2024*

| Rank | Model | Overall | Apex | LWC | Flow | Lightning Pages | Experience Cloud |
|:----:|-------|:-------:|:----:|:---:|:----:|:---------------:|:----------------:|
| 🥇 | Gemini 3 Flash | 75.0% | 100% | 100% | 50% | 0% | 100% |
| 🥈 | Gemini 2.5 Flash | 75.0% | 100% | 100% | 100% | 0% | 100% |
| 🥉 | *Your model* | [Submit →](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) |

**[📊 View detailed results →](docs/LEADERBOARD.md)**

---

## 🧪 Testing Your Model

### Supported AI Providers

| Provider | Environment Variable | Example Model |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | `gpt-4-turbo` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-3-5-sonnet-20241022` |
| Google Gemini | `GOOGLE_API_KEY` | `gemini-2.5-flash` |
| **OpenRouter** | `OPENROUTER_API_KEY` | `anthropic/claude-3.5-sonnet` |
| Ollama (local) | None needed | `codellama` |

### Quick Test

```bash
# Install
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .

# Set your API key
export OPENROUTER_API_KEY="your-key"

# Run evaluation
python scripts/evaluate.py --model my-model --tasks data/tasks/verified.json
```

### Using OpenRouter (Access 100+ Models)

OpenRouter provides unified access to Claude, GPT-4, Llama, Mistral, and more:

```python
from sfbench.utils.ai_agent import create_openrouter_agent

# Create agent with any model
agent = create_openrouter_agent(
    model="anthropic/claude-3.5-sonnet",  # or openai/gpt-4-turbo, etc.
    api_key="your-openrouter-key"
)

# Generate solution for a task
solution = agent.generate_solution(task_description="...")
```

**[See all OpenRouter models →](https://openrouter.ai/models)**

### Using Local Models (Ollama)

```bash
# Start Ollama
ollama serve

# Run with local model
python scripts/evaluate.py --model codellama --provider ollama
```

---

## 🔧 How It Works

### Validation Pipeline

```
1. LOAD TASK         → Read task from data/tasks/*.json
2. CLONE REPO        → Clone specified GitHub repo
3. APPLY SOLUTION    → Apply AI-generated patch
4. DEPLOY            → Deploy to Salesforce scratch org
5. RUN TESTS         → Execute unit tests
6. VERIFY OUTCOME    → Check functional requirements
7. REPORT RESULT     → PASS / FAIL / ERROR
```

### Validation Levels

| Level | Weight | What We Check |
|-------|:------:|---------------|
| Deployment | 30% | Solution deploys without errors |
| Unit Tests | 30% | All tests pass |
| **Functional** | 40% | **Business outcome achieved** |

### Example: Flow Validation

We don't just check if the Flow deploys. We verify it actually works:

```bash
# 1. Deploy Flow
sf project deploy start  

# 2. Create test data
sf apex run -c "Account acc = new Account(Name='Test'); insert acc; acc.Type='Customer'; update acc;"

# 3. Verify outcome
sf data query -q "SELECT Id FROM Task WHERE WhatId = :accId"
# Result: 1 Task created → PASS
# Result: 0 Tasks → FAIL
```

---

## ➕ Contributing Tasks

### Task Schema

```json
{
  "instance_id": "apex-trigger-001",
  "task_type": "APEX",
  "repo_url": "https://github.com/trailheadapps/apex-recipes",
  "base_commit": "main",
  "problem_description": "Fix the NullPointerException in AccountTriggerHandler...",
  "validation": {
    "command": "sf apex run test --class-names AccountTriggerHandlerTests",
    "expected_outcome": "Passed"
  },
  "functional_validation": {
    "description": "Verify trigger works with real data",
    "test_data_script": "data/test-scripts/apex/create_account.apex",
    "verification_query": "SELECT Description FROM Account WHERE Name = 'Test'"
  },
  "metadata": {
    "difficulty": "medium",
    "category": "apex"
  }
}
```

### Guidelines

1. Use **verified repositories** (official Salesforce sample apps)
2. Include **functional validation** - not just deployment
3. Add **test scripts** for outcome verification
4. Keep descriptions **clear and actionable**

**[See CONTRIBUTING.md →](CONTRIBUTING.md)**

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli)
- Node.js 18+ (for LWC tasks)
- Authenticated Dev Hub

### Installation

```bash
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .
```

### Run Evaluation

```bash
# With OpenRouter (recommended - access to all models)
export OPENROUTER_API_KEY="your-key"
python scripts/evaluate.py --model anthropic/claude-3.5-sonnet --tasks data/tasks/verified.json

# With Gemini
export GOOGLE_API_KEY="your-key"
python scripts/evaluate.py --model gemini-2.5-flash --tasks data/tasks/verified.json

# With local Ollama
python scripts/evaluate.py --model codellama --provider ollama --tasks data/tasks/verified.json
```

---

## 📁 Project Structure

```
sf-bench/
├── sfbench/                  # Core framework
│   ├── engine.py             # Orchestration
│   ├── runners/              # Task runners (Apex, LWC, Flow, etc.)
│   ├── validators/           # Functional validation
│   └── utils/
│       └── ai_agent.py       # AI provider integrations
├── data/
│   ├── tasks/                # Task definitions
│   │   ├── verified.json     # Main benchmark (12 tasks)
│   │   └── realistic.json    # With functional validation
│   └── test-scripts/         # Apex test scripts
├── scripts/
│   ├── evaluate.py           # Main evaluation script
│   └── leaderboard.py        # Generate leaderboard
└── docs/                     # Documentation
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Leaderboard](docs/LEADERBOARD.md) | Current benchmark results |
| [Validation Methodology](docs/REALISTIC_VALIDATION.md) | How we validate solutions |
| [Benchmark Details](docs/BENCHMARK.md) | Technical specifications |
| [Contributing](CONTRIBUTING.md) | How to contribute |

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

## 🔗 Links

- **Documentation**: [yasarshaikh.github.io/SF-bench](https://yasarshaikh.github.io/SF-bench/)
- **Issues**: [Report bugs](https://github.com/yasarshaikh/SF-bench/issues)
- **Submit Results**: [Add your model](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)

---

<p align="center">
  <strong>⭐ Star us if you find SF-Bench useful!</strong>
</p>
