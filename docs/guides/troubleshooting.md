---
layout: default
title: Troubleshooting Guide
description: Common issues and solutions for SF-Bench
---

# Troubleshooting Guide

Solutions to common SF-Bench issues.

---

## 🔧 DevHub & Authentication Issues

### Issue: "DevHub not found" or "No default DevHub set"

**Symptoms:**
```
Error: No default DevHub found
Error: DevHub alias 'DevHub' not found
```

**Solution:**
```bash
# 1. Login to your DevHub
sf org login web --alias DevHub

# 2. Set as default DevHub
sf config set target-dev-hub=DevHub

# 3. Verify
sf org list --all
# Look for (D) next to your DevHub
```

---

### Issue: Authentication expired

**Symptoms:**
```
ERROR: This org appears to have a problem with its OAuth configuration
```

**Solution:**
```bash
# Re-authenticate
sf org login web --alias DevHub --set-default-dev-hub

# Or use JWT if you have it configured
sf org login jwt --username your@email.com --jwt-key-file server.key --client-id YOUR_CLIENT_ID --set-default-dev-hub
```

---

## 🌐 Scratch Org Issues

### Issue: Scratch org creation timeout

**Symptoms:**
```
ERROR: Scratch org creation timed out after 300 seconds
ERROR: Unable to create scratch org
```

**Solution:**

```bash
# 1. Check your scratch org limits
sf org list limits --target-org DevHub

# Look for:
# - ActiveScratchOrgs: X/Y (should not be at max)
# - DailyScratchOrgs: X/Y (should not be at max)

# 2. Check active scratch orgs
sf org list scratch

# 3. Delete old/unused scratch orgs
sf org delete scratch --target-org <username> --no-prompt

# 4. If at daily limit, wait 24 hours or use a different DevHub
```

---

### Issue: Scratch org allocation exhausted

**Symptoms:**
```
ERROR: You've reached your daily scratch org allocation
```

**Solution:**

**Short-term:**
1. Use a different DevHub org
2. Wait until the next day
3. Request increased limits from Salesforce

**Long-term:**
```bash
# Contact Salesforce to increase your scratch org limits
# Or consider using multiple DevHub orgs for testing
```

---

### Issue: Invalid scratch org definition

**Symptoms:**
```
ERROR: Scratch org definition failed validation
ERROR: Invalid orgName or edition
```

**Solution:**
```bash
# Check your scratch org definition file
cat data/templates/project-scratch-def.json

# Ensure it has valid values:
{
  "orgName": "SF-Bench Test Org",
  "edition": "Developer",
  "features": ["Communities", "ServiceCloud"],
  "settings": {
    "lightningExperienceSettings": {
      "enableS1DesktopEnabled": true
    }
  }
}
```

---

## 🤖 AI Model Issues

### Issue: API key not found

**Symptoms:**
```
ERROR: OPENROUTER_API_KEY environment variable not set
ERROR: API key is required
```

**Solution:**
```bash
# Check if key is set
echo $OPENROUTER_API_KEY

# If empty, set it
export OPENROUTER_API_KEY="your-key-here"

# To make it permanent (bash):
echo 'export OPENROUTER_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc

# To make it permanent (zsh):
echo 'export OPENROUTER_API_KEY="your-key"' >> ~/.zshrc
source ~/.zshrc
```

---

### Issue: API rate limit exceeded

**Symptoms:**
```
ERROR: Rate limit exceeded
ERROR: Too many requests (429)
```

**Solution:**
```bash
# 1. Reduce parallelization
python scripts/evaluate.py --max-workers 1  # Instead of 2-4

# 2. Add delay between requests (if supported)

# 3. Use a different tier or provider
# - OpenRouter: Upgrade to paid tier
# - Gemini: Use AI Studio free tier
# - Claude: Use Anthropic direct API
```

---

### Issue: Patch application errors (malformed patches)

**Symptoms:**
```
ERROR: Failed to apply patch after trying 4 strategies
ERROR: patch: **** malformed patch at line X
```

**Solution:**

SF-Bench uses multi-strategy patch application (4 fallback methods) to handle most patch formatting issues. If all strategies fail, the patch may be fundamentally invalid.

**What SF-Bench does automatically:**
1. Strict git apply (whitespace fixes)
2. Partial application with rejects
3. 3-way merge for context mismatches
4. Fuzzy matching (SWE-bench fallback)

**If patches still fail:**
- Some models generate patches that cannot be applied even with all strategies
- This may indicate the model doesn't understand git diff format
- Try a different model or provider
- Check pre-flight checks - they validate patch format before evaluation

**Note:** Recent improvements (2025-12-30) enhanced patch cleaning to handle malformed lines (standalone `+`/`-`, empty lines). Most patch issues are now automatically handled.

---

## 📊 Evaluation Issues

### Issue: Tasks fail with "Deployment failed"

**Symptoms:**
```
ERROR: Deployment failed
Status: FAILED
```

**Solution:**
```bash
# 1. Check deployment logs
cat logs/run_evaluation/<run-id>/<model>/<task-id>/deployment.log

# 2. Common causes:
# - Missing dependencies in org
# - Invalid metadata
# - Wrong API version

# 3. Test deployment manually
sf project deploy start --target-org <scratch-org> --source-dir <path>
```

---

### Issue: Tests pass but functional validation fails

**Symptoms:**
```
Deployment: PASS ✅
Unit Tests: PASS ✅
Functional Validation: FAIL ❌
Score: 30/100
```

**Explanation:**

This is **expected** and shows the benchmark is working correctly!

**Functional validation checks:**
- Deploy: Code deploys successfully (10%)
- Unit Tests: Tests pass (20%)
- **Functional: Business outcome achieved (50%)**
- Bulk: Handles 200+ records (10%)
- No Tweaks: Works without manual fixes (10%)

If tests pass but functional validation fails, the **business outcome wasn't achieved**.

**Example:**
```
Task: "Create a Flow that creates a Task when Account Type changes to Customer"

What happened:
- Flow deployed ✅
- Tests passed ✅
- But... no Task was actually created ❌

This is a FAIL because the requirement wasn't met.
```

---

### Issue: All tasks fail with "Error"

**Symptoms:**
```
All tasks showing status: ERROR
No successful evaluations
```

**Solution:**
```bash
# 1. Check for pre-flight issues
python scripts/evaluate.py --model test --tasks data/tasks/verified.json

# 2. Verify DevHub is working
sf org list --all

# 3. Check logs for specific errors
cat logs/run_evaluation/<run-id>/*/run_instance.log

# 4. Test with a single task
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/verified.json \
  --max-workers 1
```

---

## 🐛 Installation Issues

### Issue: Package installation fails

**Symptoms:**
```
ERROR: Could not build wheels for X
ERROR: Failed building wheel for Y
```

**Solution:**
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install python3-dev build-essential

# Install system dependencies (macOS)
brew install python@3.10

# Reinstall SF-Bench
pip install -e . --force-reinstall
```

---

### Issue: Salesforce CLI not found

**Symptoms:**
```
ERROR: 'sf' command not found
ERROR: Salesforce CLI not installed
```

**Solution:**
```bash
# Install Salesforce CLI
# macOS:
brew install salesforce-cli

# Windows:
# Download from: https://developer.salesforce.com/tools/salesforcecli

# Linux:
npm install -g @salesforce/cli

# Verify installation
sf --version
```

---

## 📁 File & Path Issues

### Issue: "File not found" errors

**Symptoms:**
```
ERROR: [Errno 2] No such file or directory: 'data/tasks/verified.json'
```

**Solution:**
```bash
# 1. Check you're in the SF-Bench root directory
pwd
# Should show: .../SF bench

# 2. Verify file exists
ls data/tasks/verified.json

# 3. If missing, you may need to re-clone
git pull origin main
```

---

### Issue: Permission denied

**Symptoms:**
```
ERROR: [Errno 13] Permission denied: 'logs/...'
ERROR: Cannot create directory
```

**Solution:**
```bash
# Check permissions
ls -la logs/

# Fix permissions
chmod -R u+w logs/
chmod -R u+w results/
chmod -R u+w workspace/

# Or run as user (not root)
python scripts/evaluate.py ...
```

---

## 🔍 Debugging Tips

### Enable verbose logging

```bash
python scripts/evaluate.py \
  --model "your-model" \
  --tasks data/tasks/verified.json \
  --verbose
```

### Check specific log files

```bash
# Overall run log
cat logs/run_evaluation/<run-id>/run.log

# Task-specific logs
cat logs/run_evaluation/<run-id>/<model>/<task-id>/run_instance.log

# Scratch org creation
cat logs/run_evaluation/<run-id>/<model>/<task-id>/scratch_org.log

# Deployment output
cat logs/run_evaluation/<run-id>/<model>/<task-id>/deployment.log
```

### Test individual components

```bash
# Test DevHub connection
sf org list --all

# Test scratch org creation
sf org create scratch --definition-file data/templates/project-scratch-def.json --alias test-org

# Test AI model
python scripts/test_model.py --model "your-model"

# Test task validation
python scripts/validate_tasks.py data/tasks/verified.json
```

---

## 🆘 Still Having Issues?

If you're still stuck:

1. **Check existing issues:** [GitHub Issues](https://github.com/yasarshaikh/SF-bench/issues)
2. **Search discussions:** [GitHub Discussions](https://github.com/yasarshaikh/SF-bench/discussions)
3. **Create a new issue:** Include:
   - SF-Bench version
   - Python version (`python --version`)
   - Salesforce CLI version (`sf --version`)
   - Model being used
   - Full error message
   - Relevant log files

---

## 📚 Additional Resources

- [Quick Start Guide](../quickstart.html)
- [Full Evaluation Guide](evaluation.html)
- [FAQ](../faq.html)
- [GitHub Issues](https://github.com/yasarshaikh/SF-bench/issues)

---

*Found a solution not listed here? [Contribute it!](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md)*
