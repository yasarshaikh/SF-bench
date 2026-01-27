# Fix Lints

Fix linting and formatting issues using SF-Bench standard tools.

## Steps

1. Run Black formatter
2. Run isort for import sorting
3. Run flake8 to check remaining issues
4. Report results

## Usage

```bash
# Fix all Python files
black sfbench/ scripts/ tests/

# Sort imports
isort sfbench/ scripts/ tests/

# Check remaining issues
flake8 sfbench/ scripts/ tests/

# Full workflow
black sfbench/ scripts/ tests/ && isort sfbench/ scripts/ tests/ && flake8 sfbench/ scripts/ tests/
```

## Configuration

| Tool | Config Location | Key Settings |
|------|-----------------|--------------|
| Black | pyproject.toml | line-length = 100 |
| isort | pyproject.toml | profile = "black" |
| flake8 | (defaults) | Standard rules |

## Target Directories

- `sfbench/` - Core engine
- `scripts/` - Evaluation scripts
- `tests/` - Test suite

## Auto-Fixable Issues

- Line length violations (Black)
- Import ordering (isort)
- Trailing whitespace (Black)
- Quote style consistency (Black)

## Manual Fix Required

- Complex flake8 violations
- Type errors (mypy)
- Logic issues
- Missing docstrings
