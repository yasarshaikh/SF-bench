---
layout: default
title: FAQ - Frequently Asked Questions about SF-Bench
description: Common questions and answers about SF-Bench, Salesforce AI benchmark, evaluation methodology, model support, and troubleshooting.
keywords: sf-bench faq, salesforce benchmark questions, ai evaluation faq, salesforce ai benchmark help
---

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is SF-Bench?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SF-Bench is a benchmark for evaluating AI models on real-world Salesforce development tasks. It tests whether models can generate working Apex, Flow, and Lightning Web Component code that meets functional business requirements."
      }
    },
    {
      "@type": "Question",
      "name": "How is SF-Bench different from Salesforce's CRM benchmark?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SF-Bench focuses on evaluating AI coding agents for Salesforce development (Apex, LWC, Flow), while Salesforce's CRM benchmark evaluates AI models for business use cases (sales, service). SF-Bench tests actual code generation and execution in scratch orgs."
      }
    },
    {
      "@type": "Question",
      "name": "What do I need to run SF-Bench?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "You need: 1) Salesforce DevHub with scratch org allocation, 2) Python 3.10+, 3) Salesforce CLI (sf command), 4) API key for an AI model (OpenRouter, Gemini, Claude, etc.). See the Quick Start Guide for setup instructions."
      }
    }
  ]
}
</script>

# Frequently Asked Questions (FAQ)

Quick answers to common questions about SF-Bench.

---

## General Questions

### What is SF-Bench?

SF-Bench is a **benchmark for evaluating AI models on real-world Salesforce development tasks**. It tests whether models can generate working Apex, Flow, and Lightning Web Component code that meets functional business requirements.

### Why SF-Bench?

Existing AI benchmarks (SWE-bench, HumanEval, etc.) focus on general programming. SF-Bench focuses on **Salesforce-specific challenges**:

- Domain-specific knowledge (Salesforce APIs, governor limits, best practices)
- Multi-file solutions (Apex classes, triggers, test classes)
- Functional validation (does it actually work in a scratch org?)
- Real business outcomes (not just syntax correctness)

### Who is SF-Bench for?

- **AI researchers:** Benchmark model performance on domain-specific tasks
- **Salesforce teams:** Evaluate AI models for Salesforce development using objective metrics
- **Model providers:** Test and improve models for enterprise use cases
- **Developers:** Understand AI capabilities and limitations for Salesforce

---

## Getting Started

### What do I need to run SF-Bench?

1. **Salesforce DevHub** with scratch org allocation
2. **Python 3.10+**
3. **Salesforce CLI** (sf command)
4. **API key** for an AI model (OpenRouter, Gemini, Claude, etc.)

See the [Quick Start Guide](quickstart.html) for setup instructions.

### How long does an evaluation take?

- **Single task:** 5-10 minutes
- **Lite dataset (5 tasks):** ~30 minutes
- **Verified dataset (12 tasks):** ~1 hour
- **Full dataset (50+ tasks):** 3-5 hours

*Time varies based on scratch org creation speed and model response time.*

### How much does it cost?

**Scratch Orgs:** Free (included with Developer Edition or DevHub)

**AI Model Costs:**
- **Gemini 2.5 Flash:** Free tier available (AI Studio)
- **OpenRouter:** $0.10-$2 per evaluation (depending on model)
- **Claude Sonnet:** ~$1-3 per evaluation
- **Ollama (local):** Free (requires local GPU)

Typical cost: **$0.50-$2 per full evaluation**

---

## Technical Questions

### What tasks are included?

SF-Bench includes tasks across three categories:

1. **Apex:** Classes, triggers, bulk processing
2. **Flow:** Screen flows, record-triggered flows, scheduled flows
3. **Lightning Web Components:** UI components, event handling, data binding

See [data/tasks/verified.json](https://github.com/yasarshaikh/SF-bench/blob/main/data/tasks/verified.json) for the full list.

### How are tasks scored?

Each task is scored out of **100 points**:

- **Deploy (10%):** Code deploys successfully
- **Unit Tests (20%):** All tests pass
- **Functional (50%):** Business requirement met ← Most important!
- **Bulk Data (10%):** Handles 200+ records
- **No Manual Tweaks (10%):** Works without human fixes

A task is **RESOLVED** if:
- All tests pass
- Functional validation passes
- Score ≥ 80/100

### What is "functional validation"?

Functional validation checks if the **business outcome was achieved**, not just if the code compiles.

**Example:**
```
Task: "Create a Flow that creates a Task when Account Type changes to Customer"

❌ FAIL: Flow deploys, tests pass, but no Task is created
✅ PASS: Flow deploys, tests pass, AND Task is created
```

This is what makes SF-Bench different from syntax-only benchmarks.

### Can I add my own tasks?

Yes! SF-Bench is extensible. To add tasks:

1. Create a JSON file following the schema in `data/tasks/verified.json`
2. Include test cases for functional validation
3. Submit a PR or use it locally

See [CONTRIBUTING.md](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md) for guidelines.

---

## Model Questions

### Which models perform best?

SF-Bench measures and reports objective results. We don't make judgments about which models are "best."

See the [Leaderboard](LEADERBOARD.html) for current evaluation results and rankings.

### Why do some models fail functional validation?

Common reasons:

1. **Misunderstood requirements:** Generated code doesn't match the business logic
2. **Salesforce-specific errors:** Violates governor limits, uses deprecated APIs
3. **Incomplete solutions:** Only partial implementation (e.g., class without trigger)
4. **Test-only solutions:** Passes unit tests but doesn't work in practice

This is **expected** and shows the benchmark is challenging!

### Can I use local models (Ollama)?

Yes! SF-Bench supports Ollama for local model testing:

```bash
# Start Ollama
ollama serve

# Run evaluation
python scripts/evaluate.py --model "codellama" --provider ollama
```

Note: Local models generally have lower success rates (~20-40%) due to smaller parameter counts.

### How do I test multiple models?

Use parallel evaluation:

```bash
# Test multiple models in sequence
for model in "gemini-2.5-flash" "anthropic/claude-3.5-sonnet"; do
  python scripts/evaluate.py --model "$model" --tasks data/tasks/verified.json
done
```

For parallel evaluations, run multiple instances with different models:
```bash
# Terminal 1
python scripts/evaluate.py --model model1 --tasks data/tasks/verified.json

# Terminal 2
python scripts/evaluate.py --model model2 --tasks data/tasks/verified.json
```

---

## Results & Leaderboard

### How do I submit results to the leaderboard?

1. Run an evaluation and save results
2. Submit a GitHub issue with:
   - Model name and version
   - Evaluation date
   - Link to results JSON
   - Reproduction steps
3. We'll verify and add to the leaderboard

See [Submitting Results](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md) for details.

### Are results reproducible?

**Mostly, but not always.** Factors affecting reproducibility:

- **Model version:** Models are updated frequently
- **Temperature:** Non-zero temperature introduces randomness
- **Scratch org state:** Subtle differences in org setup
- **Timing:** Rate limits, org creation delays

For reproducibility:
- Use `temperature=0`
- Specify exact model version
- Document environment (Python, sf CLI versions)
- Run multiple times and report average

### Can I compare my results to others?

Yes! All results use a **standardized schema (v2)** for easy comparison.

Tools:
- `scripts/leaderboard.py` - Generate comparison tables
- `sfbench/utils/reporting.py` - Compare two reports

---

## Troubleshooting

### "Scratch org creation failed"

**Common causes:**
1. Daily scratch org limit reached (wait 24 hours)
2. DevHub not authenticated (re-run `sf org login`)
3. Invalid scratch org definition (check `data/templates/project-scratch-def.json`)

See [Troubleshooting Guide](guides/troubleshooting.html) for solutions.

### "API rate limit exceeded"

**Solutions:**
1. Reduce parallelization: `--max-workers 1`
2. Use a different provider (e.g., Gemini instead of OpenRouter)
3. Wait and retry

### Tasks fail with "Deployment failed"

**Common causes:**
1. Invalid Apex syntax (model generated broken code)
2. Missing dependencies (e.g., missing @future methods)
3. Test coverage too low (<75%)

Check `logs/run_evaluation/<run-id>/<model>/<task-id>/deployment.log` for details.

### Results show "ERROR" status

This means something went wrong before validation:
- Scratch org creation failed
- API error
- Patch application failed

Check `logs/run_evaluation/<run-id>/<model>/<task-id>/run_instance.log` for root cause.

---

## Advanced Usage

### Can I customize the scoring system?

Yes! Edit `sfbench/utils/schema.py`:

```python
# Change point allocation
deployment_points: int = 10  # Reduce to 5
functional_points: int = 50   # Increase to 60
```

Then re-run evaluations with the new schema.

### Can I run evaluations in CI/CD?

Yes! Example GitHub Actions workflow:

```yaml
- name: Run SF-Bench
  run: |
    python scripts/evaluate.py \
      --model "${{ matrix.model }}" \
      --tasks data/tasks/lite.json
  env:
    OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
    SF_USERNAME: ${{ secrets.DEVHUB_USERNAME }}
```

CI/CD integration guide coming soon. For now, see [Evaluation Guide](guides/evaluation.html) for running evaluations.

### How do I analyze failure patterns?

Use the reporting tools:

```python
from sfbench.utils.reporting import compare_reports, generate_markdown_summary

# Load two reports
report1 = load_report("results/model-a/report.json")
report2 = load_report("results/model-b/report.json")

# Generate comparison
comparison = compare_reports(report1, report2)
print(comparison)
```

---

## Contributing

### How can I contribute?

We welcome contributions!

- **Add tasks:** Create new Salesforce scenarios
- **Improve validation:** Enhance functional validation logic
- **Fix bugs:** Report issues or submit PRs
- **Documentation:** Improve guides and examples

See [CONTRIBUTING.md](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md) for guidelines.

### Can I use SF-Bench in my research?

Yes! SF-Bench is open source and free to use for academic research.

**Citation:**
```bibtex
@misc{sfbench2025,
  title={SF-Bench: A Benchmark for Salesforce Development Tasks},
  author={Yasar Shaikh},
  year={2025},
  url={https://github.com/yasarshaikh/SF-bench}
}
```

### How is SF-Bench different from SWE-bench?

**Similarities:**
- Real-world task focus
- Functional validation (not just syntax)
- Standardized result schema (v2, SWE-bench compatible)
- Multi-strategy patch application for robust evaluation
- Hierarchical log organization

**Differences:**
- **Domain:** Salesforce vs. Python open-source
- **Validation:** Scratch orgs vs. Docker containers
- **Tasks:** 12 verified Salesforce scenarios (expanding) vs. 2,000+ GitHub issues
- **Focus:** Enterprise development vs. open-source contributions

SF-Bench is **aligned with** SWE-bench standards and best practices, tailored for Salesforce.

---

## Future Plans

### What's coming next?

**Phase 2 (Q1 2025):**
- Lite dataset (5 tasks for quick validation)
- Enhanced analysis tools
- Web-based result viewer

**Phase 3 (Q2 2025):**
- Integration test scenarios
- Multi-org workflows
- Community task contributions

See [GitHub Issues](https://github.com/yasarshaikh/SF-bench/issues) for roadmap discussions.

### Will there be a hosted version?

We're considering a hosted version where you can:
- Run evaluations without a DevHub
- View real-time results
- Compare models instantly

Interested? [Open an issue](https://github.com/yasarshaikh/SF-bench/issues/new) to vote or discuss.

---

## Contact & Support

### Where can I get help?

- 🐛 **Bug reports:** [GitHub Issues](https://github.com/yasarshaikh/SF-bench/issues)
- 💬 **Questions:** [GitHub Issues](https://github.com/yasarshaikh/SF-bench/issues)
- 📚 **Documentation:** [docs/](https://yasarshaikh.github.io/SF-bench/)

### How do I stay updated?

- ⭐ **Star** the repo on GitHub
- 👀 **Watch** for releases
- 📧 **Subscribe** to discussions

---

## More Questions?

If your question isn't answered here:

1. Check the [Troubleshooting Guide](guides/troubleshooting.html)
2. Search [GitHub Issues](https://github.com/yasarshaikh/SF-bench/issues)
3. Ask in [GitHub Issues](https://github.com/yasarshaikh/SF-bench/issues)

---

*Last updated: December 2025*
