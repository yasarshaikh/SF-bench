---
layout: default
title: Troubleshooting Guide - Common Issues and Solutions for SF-Bench
description: Common issues and solutions for SF-Bench, including setup problems, evaluation errors, and patch application failures.
keywords: sf-bench troubleshooting, salesforce benchmark errors, ai evaluation issues, patch application fix
---

# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with SF-Bench evaluations.

## Patch Application Errors

### "unexpected end of file in patch"

**Symptom:** Patch application fails with "unexpected end of file in patch" or "corrupt patch at line X"

**Root Cause:** The AI model generated a truncated or incomplete patch. The patch is cut off mid-hunk, missing required context lines.

**Tool Behavior:**
- SF-Bench automatically detects and attempts to repair incomplete patches
- All 4 patch application strategies are attempted (strict, reject, 3-way, fuzzy)
- If all strategies fail, this indicates the patch structure is fundamentally invalid

**This is NOT a tool issue** - the benchmark correctly identified that the AI model generated an invalid patch.

**Resolution:**
- This is expected behavior when AI models generate incomplete patches
- The evaluation will mark the task as ERROR with a clear error message
- No action needed - this is a model limitation, not a tool bug

### "malformed patch at line X"

**Symptom:** Patch application fails with "malformed patch at line X"

**Root Cause:** The AI model generated a patch with invalid diff syntax (e.g., standalone `+` or `-` lines, missing context, invalid hunk headers).

**Tool Behavior:**
- SF-Bench automatically cleans common malformations (markdown fences, empty lines, etc.)
- Multiple fallback strategies are attempted
- If all strategies fail, the patch is fundamentally invalid

**This is NOT a tool issue** - the benchmark correctly identified invalid patch syntax.

**Resolution:**
- This is expected when AI models generate syntactically invalid patches
- The evaluation will mark the task as ERROR
- No action needed - this indicates the AI model needs improvement

## Scratch Org Creation Errors

### "Package ID AC - Collections" or "ancestorVersion HIGHEST can't be found"

**Symptom:** Scratch org creation fails with package dependency errors for Flow tasks

**Root Cause:** This is a **Salesforce platform limitation**, not a tool issue. Flow features may require managed packages (e.g., "AC - Collections") that are not available in Developer Edition scratch orgs.

**Tool Behavior:**
- SF-Bench correctly identifies this as a platform limitation
- Error messages clearly distinguish platform constraints from tool issues
- The evaluation will mark the task as ERROR with documentation that this is a platform limitation

**This is NOT a tool issue** - it's a known Salesforce platform constraint.

**Resolution:**
- This is a Salesforce platform limitation, not a benchmark tool failure
- Flow tasks requiring specific managed packages may fail in Developer Edition scratch orgs
- This is documented in evaluation results as a platform constraint

## Pre-flight Check Failures

### "DevHub not authenticated"

**Symptom:** Pre-flight checks fail with "DevHub not authenticated or not found"

**Resolution:**
```bash
# Authenticate with your DevHub
sf org login web --alias DevHub --instance-url <your-instance-url> --set-default-dev-hub

# Verify authentication
sf org list
```

### "API key not set"

**Symptom:** Pre-flight checks fail with "API key not configured"

**Resolution:**
1. Copy `.env.sample` to `.env`
2. Add your API keys to `.env`:
   ```bash
   ROUTELLM_API_KEY="your_key_here"
   OPENROUTER_API_KEY="your_key_here"
   # etc.
   ```
3. Ensure `.env` is in the project root directory

## Evaluation Errors

### "Evaluation failed: name 'X' is not defined"

**Symptom:** Evaluation crashes with NameError or AttributeError

**Root Cause:** This is a tool bug that needs to be fixed.

**Resolution:**
- Report this as a bug in the SF-Bench repository
- Include the full error traceback
- This is a legitimate tool issue that will be fixed

### Tasks showing ERROR status

**Understanding ERROR vs FAIL:**
- **ERROR:** Tool or platform issue (scratch org creation failed, patch application failed due to corrupt patch, etc.)
- **FAIL:** Task completed but didn't meet requirements (code deployed but tests failed, functional validation failed, etc.)

**If all tasks show ERROR:**
- Check logs for common patterns
- Verify API keys and DevHub authentication
- Check scratch org limits
- Review error messages to distinguish tool vs model issues

## Performance Issues

### Evaluation taking too long

**Possible Causes:**
- Large number of tasks
- Slow API responses from AI provider
- Scratch org creation delays
- Network issues

**Optimization:**
- Reduce `--max-workers` if system is overloaded
- Use faster AI models for testing
- Check network connectivity
- Monitor API rate limits

## Getting Help

If you encounter an issue that's not covered here:

1. **Check the logs:** Evaluation logs are in `logs/` directory with detailed error messages
2. **Review error messages:** SF-Bench clearly distinguishes tool issues from model/platform issues
3. **Report bugs:** If you believe it's a tool issue, report it with:
   - Full error traceback
   - Log file excerpts
   - Steps to reproduce
   - Environment details

## Error Message Guide

SF-Bench error messages are designed to clearly distinguish:

- **Tool Issues:** "Evaluation failed: ..." (internal errors, bugs)
- **Model Issues:** "AI model generated invalid patch" (corrupt/malformed patches)
- **Platform Limitations:** "Salesforce platform constraint" (package dependencies, org limits)

This transparency ensures vendors cannot blame the tool for model or platform limitations.
