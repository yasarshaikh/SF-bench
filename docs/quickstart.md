---
layout: default
title: Quick Start Guide - Get Started with SF-Bench in 5 Minutes
description: Complete setup guide for SF-Bench. Install, configure, and run your first evaluation in 5 minutes. Supports OpenRouter, Gemini, Claude, OpenAI, and Ollama.
keywords: sf-bench quick start, salesforce benchmark setup, ai evaluation setup, salesforce ai testing
---

# Quick Start Guide

Get SF-Bench running in **5 minutes**.

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Salesforce CLI** (sf) installed ([Install Guide](https://developer.salesforce.com/tools/salesforcecli))
- **DevHub org** with scratch org allocation
- **API key** for your chosen AI model

---

## Step 1: Install SF-Bench (2 min)

```bash
# Clone the repository
git clone https://github.com/yasarshaikh/SF-bench.git
cd SF-bench

# Install dependencies
pip install -e .
```

---

## Step 2: Authenticate with DevHub (1 min)

```bash
# Login to your DevHub
sf org login web --alias DevHub --set-default-dev-hub

# Verify connection
sf org list --all
```

You should see your DevHub marked with `(D)`.

---

## Step 3: Configure Your AI Model (1 min)

Choose your provider and set the API key:

### OpenRouter (Recommended - Access to 100+ models)
```bash
export OPENROUTER_API_KEY="your-openrouter-key-here"
```

### Google Gemini
```bash
export GOOGLE_API_KEY="your-google-api-key-here"
```

### Anthropic Claude
```bash
export ANTHROPIC_API_KEY="your-anthropic-key-here"
```

### OpenAI
```bash
export OPENAI_API_KEY="your-openai-key-here"
```

### Local Ollama (No API key needed)
```bash
ollama serve  # Start Ollama in another terminal
```

---

## Step 4: Run Your First Evaluation (1 min)

```bash
# Quick test with a single task
python scripts/evaluate.py \
  --model "gemini-2.5-flash" \
  --tasks data/tasks/verified.json \
  --max-workers 1
```

**Note:** First run may take 5-10 minutes as it creates a scratch org.

---

## Step 5: View Results

```bash
# View summary
cat evaluation_results/*/summary.md

# View detailed report
cat evaluation_results/*/report.json
```

---

## 🎉 Success!

You've run your first SF-Bench evaluation! Now you can:

### Try Different Models

```bash
# Claude Sonnet 4.5 (via OpenRouter)
python scripts/evaluate.py --model "anthropic/claude-3.5-sonnet"

# GPT-4 (via OpenRouter)
python scripts/evaluate.py --model "openai/gpt-4-turbo"

# Local model (via Ollama)
python scripts/evaluate.py --model "codellama" --provider ollama
```

### Run Full Evaluation

```bash
# Run all 12 verified tasks with functional validation
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/verified.json \
  --functional \
  --max-workers 2
```

**Time:** ~1 hour for full evaluation

### Use Lite Dataset (Coming Soon)

```bash
# Quick 5-task validation (~10 minutes)
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/lite.json \
  --max-workers 1
```

---

## Common Issues

### "DevHub not found"
```bash
# Re-authenticate
sf org login web --alias DevHub --set-default-dev-hub
```

### "Scratch org creation failed"
```bash
# Check org limits
sf org list limits --target-org DevHub

# Clean up old orgs
sf org list scratch
sf org delete scratch --target-org <username> --no-prompt
```

### "API key not found"
```bash
# Verify environment variable is set
echo $OPENROUTER_API_KEY

# Or export it again
export OPENROUTER_API_KEY="your-key"
```

---

## Next Steps

- 📖 [Full Evaluation Guide](guides/evaluation.md)
- 🔧 [Troubleshooting](guides/troubleshooting.md)
- 📊 [Understanding Results](reference/result-schema.md)
- 🏆 [Submit Your Results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)

---

## Need Help?

- 🐛 [Report Issues](https://github.com/yasarshaikh/SF-bench/issues)
- 💬 [Discussions](https://github.com/yasarshaikh/SF-bench/discussions)
- 📚 [Full Documentation](../index.md)

---

*Got through this guide in under 5 minutes? ⭐ Star us on GitHub!*
