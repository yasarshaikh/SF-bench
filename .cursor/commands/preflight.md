# Preflight

Execute preflight validation checks before running evaluations.

## Checks Performed

1. **API Key Validation** - Required provider key exists
2. **DevHub Connectivity** - Salesforce DevHub authenticated
3. **Scratch Org Limits** - Available capacity
4. **LLM Model Validation** - Model responds correctly

## Usage

```bash
# Full preflight check
python -c "
from sfbench.utils.preflight import PreflightValidator
v = PreflightValidator()
r = v.run_all_checks('model-name', 'provider')
print('PASSED' if r.passed else 'FAILED')
for c in r.checks:
    print(f'{c.name}: {c.status}')
"
```

## Check Details

### API Key Check
- Verifies environment variable exists
- Provider-specific: `ROUTELLM_API_KEY`, `OPENROUTER_API_KEY`, `GOOGLE_API_KEY`

### DevHub Check
- Verifies `sf org list` returns DevHub
- Required for scratch org creation

### Scratch Org Limits
- Checks active org count vs limit
- Warns at 80% capacity

### LLM Model Check
- Tests model availability
- Validates response format

## Output

```
✅ API Key: PASSED
✅ DevHub: PASSED
⚠️ Scratch Org Limits: WARNING (75% capacity)
✅ LLM Model: PASSED

Overall: PASSED (with warnings)
```

## Troubleshooting

| Check | Failure | Fix |
|-------|---------|-----|
| API Key | Missing | Set environment variable |
| DevHub | Not found | `sf org login web -d` |
| Scratch Limits | Exceeded | Delete orgs or wait |
| LLM Model | Failed | Check provider status |
