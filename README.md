# SF-Bench: The Salesforce AI Benchmark

<p align="center">
  <img src="https://img.shields.io/badge/SF--Bench-Salesforce%20AI%20Benchmark-00A1E0?style=for-the-badge&logo=salesforce&logoColor=white" alt="SF-Bench"/>
  <br>
  <a href="https://github.com/yasarshaikh/SF-bench/stargazers"><img src="https://img.shields.io/github/stars/yasarshaikh/SF-bench?style=social" alt="GitHub stars"/></a>
  <a href="https://github.com/yasarshaikh/SF-bench/network/members"><img src="https://img.shields.io/github/forks/yasarshaikh/SF-bench?style=social" alt="GitHub forks"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"/></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"/></a>
  <a href="https://yasarshaikh.github.io/SF-bench/"><img src="https://img.shields.io/badge/docs-live-brightgreen.svg" alt="Documentation"/></a>
</p>

<p align="center">
  <strong>The Open Benchmark for Evaluating AI Coding Agents on Salesforce Development</strong>
  <br>
  <em>Objective measurement. Real execution. Verified results.</em>
</p>

---

## 🎯 I Am A...

**Choose your path:**

| 👤 I'm... | 🎯 I Want To... | ➡️ Go To... |
|-----------|-----------------|------------|
| **New to SF-Bench** | Understand what this is | [What is SF-Bench?](docs/getting-started/what-is-sf-bench.md) |
| **New to Salesforce** | Learn about Salesforce | [What is Salesforce?](docs/getting-started/what-is-salesforce.md) |
| **Company/Enterprise** | Evaluate AI tools for my team | [For Companies](docs/personas/for-companies.md) |
| **Salesforce Developer** | Test AI models on Salesforce | [Quick Start](docs/quickstart.md) |
| **Researcher** | Benchmark AI models | [Evaluation Guide](docs/guides/evaluation.md) |
| **SWE-bench User** | Compare with SWE-bench | [Comparison](docs/evaluation/comparison-with-swe-bench.md) |
| **Open Source Enthusiast** | Contribute to SF-Bench | [Contributing](CONTRIBUTING.md) |

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Install
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .

# 2. Set API key
export OPENROUTER_API_KEY="your-key"

# 3. Run evaluation
python scripts/evaluate.py --model anthropic/claude-3.5-sonnet --tasks data/tasks/verified.json
```

**📖 [Full Quick Start Guide →](docs/quickstart.md)**

---

## 🏆 Current Leaderboard

*Results as of December 2025*

| Rank | Model | Overall | Functional Score | LWC | Deploy | Apex | Flow |
|:----:|-------|:-------:|:----------------:|:---:|:------:|:----:|:----:|
| 🥇 | **Claude Sonnet 4.5** | **41.67%** | **6.0%** | 100% | 100% | 100% | 0%* |
| 🥈 | **Gemini 2.5 Flash** | **25.0%** | - | 100% | 100% | 0%* | 0%* |

*\* Flow tasks failed due to scratch org creation issues (being fixed)*

**[📊 View Full Leaderboard →](docs/LEADERBOARD.md)**

---

## 🎯 What is SF-Bench?

SF-Bench is an **open, objective benchmark** for measuring how well AI coding agents perform on Salesforce development tasks.

### Why Salesforce-Specific?

Generic benchmarks (HumanEval, SWE-bench) miss Salesforce-specific challenges:

| Challenge | What We Test |
|-----------|--------------|
| **Multi-modal development** | Apex, LWC (JavaScript), Flows (XML), Metadata |
| **Platform execution** | Real scratch orgs, not just syntax checks |
| **Governor limits** | CPU time, SOQL queries, heap size |
| **Declarative tools** | Flows, Lightning Pages, Permission Sets |
| **Enterprise patterns** | Triggers, batch jobs, integrations |

### We Are Auditors, Not Predictors

- ✅ Measure actual performance
- ✅ Report objective results  
- ✅ Verify functional outcomes
- ❌ Don't predict what models "should" score
- ❌ Don't claim expected success rates

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

### Validation Levels (Weighted Scoring: 0-100 points)

| Level | Weight | What We Check |
|-------|:------:|---------------|
| Deployment | 10% | Solution deploys without errors |
| Unit Tests | 20% | All tests pass, coverage ≥80% |
| **Functional** | **50%** | **Business outcome achieved** |
| Bulk Operations | 10% | Handles 200+ records |
| No Manual Tweaks | 10% | Works in one shot |

---

## 🧪 Testing Your Model

### Supported AI Providers

| Provider | Environment Variable | Example Model |
|----------|---------------------|---------------|
| **OpenRouter** | `OPENROUTER_API_KEY` | `anthropic/claude-3.5-sonnet` |
| **RouteLLM** | `ROUTELLM_API_KEY` | `gemini-3-flash-preview` |
| OpenAI | `OPENAI_API_KEY` | `gpt-4-turbo` |
| Anthropic | `ANTHROPIC_API_KEY` | `claude-3-5-sonnet-20241022` |
| Google Gemini | `GOOGLE_API_KEY` | `gemini-2.5-flash` |
| Ollama (local) | None needed | `codellama` |

### Quick Test

```bash
# With OpenRouter (recommended - access to 100+ models)
export OPENROUTER_API_KEY="your-key"
python scripts/evaluate.py --model anthropic/claude-3.5-sonnet --tasks data/tasks/verified.json

# With Gemini
export GOOGLE_API_KEY="your-key"
python scripts/evaluate.py --model gemini-2.5-flash --tasks data/tasks/verified.json

# With local Ollama
python scripts/evaluate.py --model codellama --provider ollama --tasks data/tasks/verified.json
```

---

## 📊 Task Categories

SF-Bench includes **12 verified tasks** across Salesforce development domains:

| Category | Tasks | Description | Lite Dataset |
|----------|:-----:|-------------|:------------:|
| **Apex** | 2 | Triggers, Classes, Integrations | ✅ |
| **LWC** | 2 | Lightning Components | ✅ |
| **Flow** | 2 | Record-Triggered Flows, Invocable Actions | ✅ |
| **Lightning Pages** | 1 | Dynamic Forms | ✅ |
| **Experience Cloud** | 1 | Guest Access | ❌ |
| **Architecture** | 4 | Full-stack Design | ✅ |

### Datasets

- **Lite (5 tasks):** Quick validation in ~10 minutes - `data/tasks/lite.json`
- **Verified (12 tasks):** Full evaluation in ~1 hour - `data/tasks/verified.json`
- **Realistic:** Challenging scenarios - `data/tasks/realistic.json`

---

## 📖 Documentation

### Getting Started
- 🚀 [Quick Start Guide](docs/quickstart.md) - Get running in 5 minutes
- 📚 [What is SF-Bench?](docs/getting-started/what-is-sf-bench.md) - Complete overview
- 🏢 [What is Salesforce?](docs/getting-started/what-is-salesforce.md) - For beginners
- ❓ [FAQ](docs/faq.md) - Common questions

### For Different Audiences
- 💼 [For Companies](docs/personas/for-companies.md) - Business case & ROI
- 👨‍💻 [For Salesforce Developers](docs/guides/evaluation.md) - Evaluation guide
- 🔬 [For Researchers](docs/VALIDATION_METHODOLOGY.md) - Methodology details
- 🔄 [SWE-bench Comparison](docs/evaluation/comparison-with-swe-bench.md) - Benchmark comparison

### Reference
- 📋 [Validation Methodology](docs/VALIDATION_METHODOLOGY.md) - How we validate
- 📊 [Benchmark Details](docs/BENCHMARK.md) - Technical specifications
- 🏆 [Full Leaderboard](docs/LEADERBOARD.md) - Complete model rankings
- 📄 [Result Schema](docs/reference/result-schema.md) - Result format

### Contributing
- ➕ [Contributing Guide](CONTRIBUTING.md) - How to contribute
- 🎯 [Task Guidelines](docs/guides/task-guidelines.md) - Creating new tasks
- 📊 [Submitting Results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)

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
│   │   ├── lite.json         # Quick validation (5 tasks)
│   │   └── realistic.json   # Challenging scenarios
│   └── test-scripts/         # Apex test scripts
├── scripts/
│   ├── evaluate.py           # Main evaluation script
│   └── leaderboard.py       # Generate leaderboard
└── docs/                     # Documentation
    ├── getting-started/      # Beginner guides
    ├── personas/             # Persona-specific content
    ├── evaluation/           # Evaluation guides
    └── reference/            # Technical reference
```

---

## 🤝 Get Involved

| Action | Link |
|--------|------|
| ⭐ **Star** the repo | [GitHub](https://github.com/yasarshaikh/SF-bench) |
| 📊 **Submit** results | [Submit Results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) |
| 🐛 **Report** bugs | [Issues](https://github.com/yasarshaikh/SF-bench/issues) |
| ➕ **Add** tasks | [Contributing](CONTRIBUTING.md) |
| 💬 **Discuss** | [Discussions](https://github.com/yasarshaikh/SF-bench/discussions) |

---

## 🔗 Links

- **📖 Documentation**: [yasarshaikh.github.io/SF-bench](https://yasarshaikh.github.io/SF-bench/)
- **🐙 GitHub**: [github.com/yasarshaikh/SF-bench](https://github.com/yasarshaikh/SF-bench)
- **📊 Leaderboard**: [View Results](docs/LEADERBOARD.md)
- **❓ Issues**: [Report Bugs](https://github.com/yasarshaikh/SF-bench/issues)

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Inspired by [SWE-bench](https://www.swebench.com/) methodology
- Built with [Salesforce CLI](https://developer.salesforce.com/tools/salesforcecli)
- Uses official [Salesforce sample apps](https://github.com/trailheadapps)

---

<p align="center">
  <strong>⭐ Star us if you find SF-Bench useful!</strong>
  <br>
  <em>Help us build the best Salesforce AI benchmark</em>
</p>
