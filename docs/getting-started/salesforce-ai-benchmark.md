---
layout: default
title: Salesforce AI Benchmark Guide
description: Learn what a Salesforce AI benchmark is, why SF-Bench matters, and how to run trusted evaluations for Apex, Flow, and Lightning development.
permalink: /salesforce-ai-benchmark/
keywords: salesforce ai benchmark, salesforce benchmark guide, apex benchmark, lightning web component benchmark, salesforce ai evaluation, sf-bench overview
---

# Salesforce AI Benchmark Guide

**Understand why Salesforce teams, AI researchers, and platform vendors rely on SF-Bench to evaluate coding agents.**

---

## Why Salesforce Needs Its Own AI Benchmark

Generic coding benchmarks (HumanEval, SWE-bench) rarely capture the realities of Salesforce development:

- **Multi-artifact delivery:** Real solutions span Apex classes, triggers, Lightning Web Components, Flows, metadata, and declarative configs.
- **Platform limits:** Governor limits, security requirements, and dependency ordering often break naive AI output.
- **Functional validation:** Deploying code is not enough; teams must prove that business outcomes occur inside a scratch org.

SF-Bench is purpose-built to close that gap with domain-specific tasks, verified scripts, and repeatable scoring.

---

## What SF-Bench Measures

| Layer | What We Validate | Why It Matters |
|-------|------------------|----------------|
| **Deployment** | Metadata deploys to a fresh scratch org | Confirms generated artifacts compile and can be installed |
| **Unit & Integration Tests** | Auto-generated or provided tests pass | Ensures code integrity and coverage |
| **Functional Outcomes** | Business requirement succeeds via CLI checks | Captures real-world success criteria |
| **Bulk & Resilience** | Tasks run at scale without governor violations | Proves readiness for enterprise workloads |

👉 See the [Validation Methodology](../VALIDATION_METHODOLOGY.html) for the exact scoring rubric.

---

## Datasets for Every Journey

| Dataset | Tasks | Time | Perfect For |
|---------|:----:|:----:|-------------|
| **Lite** (`data/tasks/lite.json`) | 5 | ~10 min | Quick proof-of-concept, demos |
| **Verified** (`data/tasks/verified.json`) | 12 | ~60 min | Official leaderboard submissions |
| **Realistic** (`data/tasks/realistic.json`) | 30+ | 2-3 hrs | Deep vendor or research evaluations |

Each dataset ships with task prompts, acceptance tests, and validation scripts so that results remain comparable across runs.

---

## How to Run a Salesforce AI Benchmark in 5 Steps

1. **Install & Authenticate**  
   Follow the [Quick Start](../quickstart.html) to install SF-Bench, log in to your DevHub, and set API keys.
2. **Select a Dataset**  
   Start with `data/tasks/lite.json` for a rapid sanity check, then graduate to `data/tasks/verified.json` for leaderboard-ready numbers.
3. **Pick a Model Provider**  
   Use RouteLLM, OpenRouter, Google Gemini, Anthropic, OpenAI, or local Ollama models. Set the appropriate environment variables.
4. **Run Evaluate Script**  
   ```bash
   python scripts/evaluate.py \
     --model "anthropic/claude-3.5-sonnet" \
     --tasks data/tasks/verified.json \
     --functional \
     --max-workers 2
   ```
5. **Review Reports**  
   SF-Bench emits JSON + Markdown summaries under `results/` and `evaluation_results/` for easy sharing, diffing, and submissions.

Need more detail? Jump to the [Evaluation Guide](../guides/evaluation.html) for advanced orchestration tips.

---

## Comparing SF-Bench to SWE-bench

| Area | SF-Bench | SWE-bench |
|------|----------|-----------|
| **Domain** | Salesforce (Apex, LWC, Flow) | Python OSS issues |
| **Execution** | Scratch orgs, CLI validators | Docker containers |
| **Functional Checks** | Business outcome verification | Patch applies + tests |
| **Audience** | Enterprises, Salesforce partners, AI vendors | General-purpose LLM researchers |

Read the full [comparison guide](../evaluation/comparison-with-swe-bench.html) to understand why both benchmarks complement each other.

---

## Use Cases

- **Salesforce COEs:** Compare multiple AI copilots before rolling out to thousands of admins and developers.
- **Model Vendors:** Publish transparent Salesforce-specific scores to win enterprise trust.
- **Researchers:** Stress-test agent frameworks on metadata-heavy, multi-step deployments.
- **Consultants & ISVs:** Validate that accelerators and packaged AI assistants meet client-grade standards.

---

## Results & Submissions

1. Explore the live [Leaderboard](../LEADERBOARD.html) for current model standings.
2. Package your `report.json` and `summary.md` from `evaluation_results/`.
3. [Submit results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) with reproduction steps and model metadata.

Every accepted submission improves community trust and builds the public record for Salesforce AI benchmarking.

---

## Resources & Next Steps

- 📚 [What is SF-Bench?](what-is-sf-bench.html)
- 🚀 [Quick Start Guide](../quickstart.html)
- 🧪 [Evaluation Guide](../guides/evaluation.html)
- 🧰 [Troubleshooting](../guides/troubleshooting.html)
- 🧾 [Result Schema Reference](../reference/result-schema.html)

✨ Need talking points for stakeholders? Share this page or link directly using `/salesforce-ai-benchmark/` for an easy-to-remember URL.
