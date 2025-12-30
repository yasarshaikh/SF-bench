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

### Required Software

- **Python 3.10+** installed ([Download](https://www.python.org/downloads/))
- **Salesforce CLI** (`sf`) installed ([Install Guide](https://developer.salesforce.com/tools/salesforcecli))
- **DevHub org** with scratch org allocation ([Create DevHub](https://developer.salesforce.com/signup))

### API Key Requirements

You need an API key from one of these providers:

| Provider | Environment Variable | Example Models | Where to Get |
|----------|---------------------|----------------|--------------|
| **RouteLLM** | `ROUTELLM_API_KEY` | Grok 4.1, GPT-5, Claude Opus 4 | [RouteLLM Dashboard](https://routellm.com) |
| **OpenRouter** | `OPENROUTER_API_KEY` | Claude Sonnet, GPT-4, Llama | [OpenRouter Keys](https://openrouter.ai/keys) |
| **Google Gemini** | `GOOGLE_API_KEY` | Gemini 2.5 Flash, Gemini Pro | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| **Anthropic** | `ANTHROPIC_API_KEY` | Claude 3.5 Sonnet, Claude Opus | [Anthropic Console](https://console.anthropic.com) |
| **OpenAI** | `OPENAI_API_KEY` | GPT-4, GPT-3.5 | [OpenAI Platform](https://platform.openai.com/api-keys) |

### Resource Requirements

**For Full Evaluation (12 tasks with `--functional`):**
- **Scratch Orgs:** 
  - Minimum: **1 org** (with `--max-workers 1`, sequential execution)
  - Recommended: **2-3 orgs** (with `--max-workers 2-3`, balanced speed)
  - Maximum: **5 orgs** (with `--max-workers 5`, fastest but needs more capacity)
  - **Note:** Each worker needs its own scratch org. Total tasks = 12, so you'll create 12 orgs sequentially or in parallel based on workers.
- **Token Usage:** 
  - Per task: ~8,000 tokens (input prompt + generated code + context)
  - Full evaluation: ~96,000 tokens (~0.1M tokens)
- **Time:** 1-2 hours (depends on scratch org creation speed and model response time)
- **Cost:** $0.10-$2 per evaluation (varies by model and provider)

**For Lite Evaluation (5 tasks):**
- **Scratch Orgs:** 1-3 orgs
- **Token Usage:** ~40,000 tokens
- **Time:** ~10-15 minutes

**System Requirements:**
- **Max Workers:** Supports up to 5 workers (based on typical DevHub limits)
- **Network:** Stable internet connection for API calls and scratch org creation
- **Disk Space:** ~500MB for workspace and cloned repositories

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

- 📖 [Full Evaluation Guide](guides/evaluation.html)
- 🔧 [Troubleshooting](guides/troubleshooting.html)
- 📊 [Understanding Results](reference/result-schema.html)
- 🏆 [Submit Your Results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)

---

## Need Help?

- 🐛 [Report Issues](https://github.com/yasarshaikh/SF-bench/issues)
- 💬 [Discussions](https://github.com/yasarshaikh/SF-bench/discussions)
- 📚 [Full Documentation](../)

---

*Got through this guide in under 5 minutes? ⭐ Star us on GitHub!*
