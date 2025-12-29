---
layout: default
title: What is SF-Bench? - Complete Overview
description: Learn what SF-Bench is, how it works, and why it matters. Perfect for first-time visitors.
keywords: what is sf-bench, salesforce benchmark explained, ai benchmark overview
---

# What is SF-Bench?

**SF-Bench** is the first comprehensive benchmark for evaluating AI coding agents on **real-world Salesforce development tasks**.

---

## 🎯 The Problem SF-Bench Solves

### Generic Benchmarks Fall Short

Existing AI benchmarks (like HumanEval, SWE-bench) test general programming, but miss **Salesforce-specific challenges**:

❌ **They don't test**:
- Platform-specific constraints (governor limits)
- Multi-modal development (Apex + LWC + Flow)
- Real Salesforce execution (scratch orgs)
- Business logic validation

✅ **SF-Bench does**:
- Tests in real Salesforce environments
- Validates functional outcomes (not just syntax)
- Covers all Salesforce development types
- Measures production-ready code

---

## 🔍 What SF-Bench Does

### 1. **Provides Real Tasks**
- 12+ verified Salesforce development tasks
- Based on real-world scenarios
- From official Salesforce sample apps

### 2. **Evaluates AI Models**
- Tests how well AI generates Salesforce code
- Measures functional correctness
- Reports objective results

### 3. **Reports Results**
- Leaderboard of model performance
- Detailed breakdowns by task type
- Functional validation scores

---

## 🏗️ How It Works

### The Evaluation Process

```
1. Task Definition
   ↓
2. AI Generates Solution
   ↓
3. Deploy to Salesforce Scratch Org
   ↓
4. Run Unit Tests
   ↓
5. Verify Functional Outcome
   ↓
6. Score & Report
```

### What Gets Tested

| Task Type | What It Tests |
|-----------|---------------|
| **Apex** | Backend code (triggers, classes) |
| **LWC** | Frontend components (JavaScript) |
| **Flow** | Visual automation |
| **Lightning Pages** | UI configuration |
| **Experience Cloud** | Public-facing sites |
| **Architecture** | Full-stack solutions |

---

## 📊 Scoring System

### Weighted Validation (0-100 points)

| Component | Weight | What It Checks |
|-----------|:------:|----------------|
| **Deployment** | 10% | Code deploys successfully |
| **Unit Tests** | 20% | All tests pass, coverage ≥80% |
| **Functional** | **50%** | **Business outcome achieved** |
| **Bulk Operations** | 10% | Handles 200+ records |
| **No Manual Tweaks** | 10% | Works in one shot |

**Key**: Functional validation (50%) ensures the solution **actually works**, not just compiles.

---

## 🎯 Who Uses SF-Bench?

### 1. **AI Researchers**
- Benchmark model performance
- Compare different models
- Research AI capabilities

### 2. **Companies**
- Evaluate AI tools for Salesforce development
- Choose the best AI coding assistant
- Measure ROI of AI tools

### 3. **Salesforce Developers**
- Understand AI capabilities
- Choose AI tools
- Learn best practices

### 4. **Model Providers**
- Test and improve models
- Showcase capabilities
- Competitive benchmarking

---

## 🆚 SF-Bench vs. Other Benchmarks

### vs. HumanEval
- **HumanEval**: General Python programming
- **SF-Bench**: Salesforce-specific, real execution

### vs. SWE-bench
- **SWE-bench**: Open-source Python projects
- **SF-Bench**: Salesforce platform, enterprise focus

### vs. CodeXGLUE
- **CodeXGLUE**: Multiple languages, syntax-focused
- **SF-Bench**: Salesforce-only, functional validation

---

## ✅ Why SF-Bench Matters

### 1. **Real-World Relevance**
- Tests actual Salesforce development
- Validates functional outcomes
- Production-ready code

### 2. **Objective Measurement**
- No predictions or claims
- Just facts and results
- Transparent methodology

### 3. **Comprehensive Coverage**
- All Salesforce development types
- Multiple difficulty levels
- Real-world scenarios

### 4. **Open & Accessible**
- Open source (MIT license)
- Free to use
- Community-driven

---

## 🚀 Getting Started

### Quick Start (5 minutes)

```bash
# 1. Install
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench
pip install -e .

# 2. Set API key
export OPENROUTER_API_KEY="your-key"

# 3. Run evaluation
python scripts/evaluate.py --model anthropic/claude-3.5-sonnet
```

### What You Need

- Python 3.10+
- Salesforce CLI
- DevHub org (free)
- AI model API key

**[Full Quick Start Guide →](../quickstart.md)**

---

## 📖 Learn More

### For Beginners
- [What is Salesforce?](what-is-salesforce.md) - If you're new to Salesforce
- [Quick Start Guide](../quickstart.md) - Get running in 5 minutes
- [FAQ](../faq.md) - Common questions

### For Companies
- [For Companies](../personas/for-companies.md) - Business case and ROI
- [Comparison with Competitors](../evaluation/comparison-with-swe-bench.md) - Benchmark comparison

### For Developers
- [Evaluation Guide](../guides/evaluation.md) - Complete guide
- [Validation Methodology](../VALIDATION_METHODOLOGY.md) - How we validate
- [Task Schema](../reference/task-schema.md) - Technical details

### For Researchers
- [Methodology](../VALIDATION_METHODOLOGY.md) - Detailed methodology
- [Benchmark Details](../BENCHMARK.md) - Technical specifications
- [Result Schema](../reference/result-schema.md) - Result format

---

## 🏆 Current Results

See which models perform best: **[Leaderboard →](../LEADERBOARD.md)**

---

## 🤝 Get Involved

- ⭐ **Star** the repo
- 📊 **Submit** your model's results
- ➕ **Contribute** tasks
- 🐛 **Report** bugs
- 💬 **Join** discussions

**[GitHub Repository →](https://github.com/yasarshaikh/SF-bench)**

---

**Ready to start?** Check out our [Quick Start Guide](../quickstart.md)!
