---
layout: default
title: SF-Bench - Salesforce AI Benchmark
description: The open benchmark for evaluating AI coding agents on Salesforce development. Objective measurement, real execution, verified results.
---

# SF-Bench: The Salesforce AI Benchmark

**The open, objective benchmark for measuring AI coding agents on Salesforce development tasks.**

---

## 📌 Quick Navigation

| I want to... | Link |
|--------------|------|
| 🏆 See results | [Leaderboard](#-leaderboard) |
| 🧪 Test my model | [Testing Your Model](#-testing-your-model) |
| ➕ Add tasks | [Contributing](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md) |
| 📊 Submit results | [Submit Results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) |

---

## 🎯 What We Do

SF-Bench **measures and reports**. We don't predict or claim expected outcomes.

| We Do | We Don't |
|-------|----------|
| ✅ Measure actual performance | ❌ Predict success rates |
| ✅ Report objective results | ❌ Claim what models "should" score |
| ✅ Verify functional outcomes | ❌ Interpret or editorialize |
| ✅ Test in real Salesforce orgs | ❌ Just check syntax |

---

## 🏆 Leaderboard

*December 2024*

| Rank | Model | Overall | Apex | LWC | Flow | Lightning Pages |
|:----:|-------|:-------:|:----:|:---:|:----:|:---------------:|
| 🥇 | Gemini 3 Flash | 75.0% | 100% | 100% | 50% | 0% |
| 🥈 | Gemini 2.5 Flash | 75.0% | 100% | 100% | 100% | 0% |
| 🥉 | *Your model* | [Submit](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) | | | | |

**[Full Leaderboard →](LEADERBOARD.md)**

---

## 🧪 Testing Your Model

### Supported Providers

| Provider | Models | Setup |
|----------|--------|-------|
| **OpenRouter** | 100+ models | `OPENROUTER_API_KEY` |
| OpenAI | GPT-4, GPT-3.5 | `OPENAI_API_KEY` |
| Anthropic | Claude 3.5, 3 | `ANTHROPIC_API_KEY` |
| Google | Gemini 2.5, Pro | `GOOGLE_API_KEY` |
| Ollama | Local models | No key needed |

### Quick Start

```bash
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .

# Run with OpenRouter (access to all models)
export OPENROUTER_API_KEY="your-key"
python scripts/evaluate.py --model anthropic/claude-3.5-sonnet

# Run with Gemini
export GOOGLE_API_KEY="your-key"
python scripts/evaluate.py --model gemini-2.5-flash

# Run with local Ollama
python scripts/evaluate.py --model codellama --provider ollama
```

---

## 🔧 How Validation Works

### We Check Outcomes, Not Just Deployment

```
Standard Benchmark:
  Deploy succeeded? → PASS ✅
  
SF-Bench:
  Deploy succeeded? → Step 1 of 3
  Tests passed? → Step 2 of 3
  Business outcome achieved? → Step 3 of 3 → PASS/FAIL
```

### Example: Flow Task

```bash
# Step 1: Deploy
sf project deploy start  # ✅

# Step 2: Create test data
sf apex run -c "insert new Account(Name='Test', Type='Customer');"

# Step 3: Verify outcome
sf data query -q "SELECT Id FROM Task WHERE WhatId = :accId"
# 1 Task created → PASS
# 0 Tasks → FAIL (Flow didn't work)
```

---

## 📊 Task Categories

| Category | Tasks | Description |
|----------|:-----:|-------------|
| Apex | 2 | Triggers, Classes |
| LWC | 2 | Lightning Components |
| Flow | 2 | Record-Triggered Flows |
| Lightning Pages | 1 | Dynamic Forms |
| Experience Cloud | 1 | Guest Access |
| Architecture | 4 | Full-stack Design |

---

## 📖 Documentation

- [Validation Methodology](REALISTIC_VALIDATION.md)
- [Benchmark Details](BENCHMARK.md)
- [Leaderboard](LEADERBOARD.md)
- [Contributing](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md)

---

## 🤝 Get Involved

| Action | Link |
|--------|------|
| ⭐ Star the repo | [GitHub](https://github.com/yasarshaikh/SF-bench) |
| 📊 Submit results | [Submit](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) |
| 🐛 Report bugs | [Issues](https://github.com/yasarshaikh/SF-bench/issues) |
| ➕ Add tasks | [Contributing](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md) |

---

**⭐ Star us on GitHub if you find SF-Bench useful!**
