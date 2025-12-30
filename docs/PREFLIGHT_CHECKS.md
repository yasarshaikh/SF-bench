# Pre-Flight Checks

SF-Bench now includes comprehensive pre-flight validation to prevent wasted time, resources, and API costs.

## What Gets Checked

### 1. DevHub Connectivity ✅
- Verifies DevHub authentication
- Checks if authenticated orgs are accessible
- **Failure**: Prevents scratch org creation failures

### 2. Scratch Org Limits 📊
- Checks available scratch org capacity vs. required
- Estimates daily and active limits (Enterprise Edition: 80 daily, 40 active)
- Warns if approaching limits (80%+ capacity)
- **Failure**: Prevents "LIMIT_EXCEEDED" errors mid-evaluation

### 3. API Key Configuration 🔑
- Verifies required API keys are set
- Checks provider-specific keys (ROUTELLM_API_KEY, OPENROUTER_API_KEY, etc.)
- **Failure**: Prevents API authentication errors

### 4. LLM Model Validation 🤖
- Verifies model exists on the provider
- Tests model format generation (curl test)
- Validates that model generates proper git diff format
- **Failure**: Prevents format issues like Gemini 3 Flash or corrupt patches like GPT 5.2

## Usage

### Basic Usage (Automatic Checks)
```bash
python scripts/evaluate.py --model gpt-5.2 --tasks data/tasks/verified.json --functional
```

Pre-flight checks run automatically and will:
- ✅ Pass → Continue with evaluation
- ❌ Fail → Exit with clear error messages

### Interactive Mode
```bash
python scripts/evaluate.py --model gpt-5.2 --tasks data/tasks/verified.json --functional --interactive
```

If checks fail, interactive mode will:
- Prompt for missing API keys
- Guide you through DevHub authentication
- Re-run checks after setup

### Skip Checks (Not Recommended)
```bash
python scripts/evaluate.py --model gpt-5.2 --tasks data/tasks/verified.json --skip-preflight
```

⚠️ **Warning**: Skipping checks may lead to:
- Wasted API costs
- Scratch org limit errors
- Format validation failures

### Skip LLM Format Check (Faster)
```bash
python scripts/evaluate.py --model gpt-5.2 --tasks data/tasks/verified.json --skip-llm-check
```

Useful when you've already verified the model format works.

## Example Output

```
======================================================================
🔍 PRE-FLIGHT CHECKS
======================================================================

📋 Check Results:
  ✅ api_key: ✅ ROUTELLM_API_KEY configured
  ✅ devhub: DevHub authenticated and accessible
  ✅ scratch_org_limits: ✅ Sufficient capacity: ~35 scratch orgs available (estimated)
  ✅ llm_model: ✅ Model 'gpt-5.2' available and generates valid diff format

✅ All pre-flight checks passed!
======================================================================
```

## Benefits

1. **Prevents Wasted Resources**: Catch issues before expensive operations
2. **Clear Error Messages**: Know exactly what's wrong and how to fix it
3. **Interactive Setup**: Guided configuration for missing details
4. **Format Validation**: Catch model format issues early (like Gemini 3 Flash)
5. **Scratch Org Management**: Avoid hitting limits mid-evaluation

## Implementation Details

Pre-flight checks are implemented in `sfbench/utils/preflight.py`:

- `PreflightValidator`: Main validation class
- `check_devhub_connectivity()`: DevHub verification
- `check_scratch_org_limits()`: Capacity checking
- `check_llm_model()`: Model format validation
- `interactive_setup()`: Interactive configuration prompts

## Next Steps

After pre-flight checks pass, the evaluation proceeds normally:
1. Generate solutions (if not pre-provided)
2. Create scratch org (if needed)
3. Run tasks with validation
4. Calculate scores
5. Generate results

---

*Last updated: 2025-12-30*
