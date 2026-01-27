# Test

Execute test suites for SF-Bench codebase.

## Steps

1. Verify pytest is installed
2. Run pytest with specified options
3. Generate coverage report if enabled
4. Report results

## Usage

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_checkpoint.py

# Run with coverage
pytest --cov=sfbench --cov-report=term-missing

# Run specific test function
pytest tests/test_checkpoint.py::test_create_checkpoint
```

## Coverage Targets

| Module | Target | Notes |
|--------|--------|-------|
| Core engine | 90%+ | Critical path |
| Runners | 80%+ | Task-specific |
| Utils | 75%+ | Helper functions |
| Overall | 80%+ | Project standard |

## Test Structure

```
tests/
├── test_audit_logging.py    # Audit trail tests
├── test_checkpoint.py       # Checkpoint management
├── test_config.py           # Configuration tests
├── test_patch_validation.py # Patch handling
├── test_retry.py            # Retry logic
└── test_schema_verification.py # Schema tests
```

## Output

- Test results: stdout
- Coverage report: terminal or HTML
- Exit code: 0 (pass) or 1 (fail)
