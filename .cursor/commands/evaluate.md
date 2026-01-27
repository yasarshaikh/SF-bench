# Evaluate

Execute SF-Bench evaluation workflows for AI model testing.

## Steps

1. Run preflight checks to verify prerequisites
2. Load tasks from specified file
3. Generate solutions via AI provider (if not pre-generated)
4. Execute evaluation pipeline (deploy → validate → score)
5. Run functional validation if enabled
6. Generate reports (JSON + Markdown)
7. Cleanup scratch orgs

## Usage

```bash
# Basic evaluation
python scripts/evaluate.py --model <model> --tasks data/tasks/verified.json

# With functional validation
python scripts/evaluate.py --model <model> --tasks data/tasks/verified.json --functional

# With pre-generated solutions
python scripts/evaluate.py --model <model> --tasks data/tasks/verified.json --solutions solutions/<model>/

# Resume from checkpoint
python scripts/evaluate.py --model <model> --tasks data/tasks/verified.json --output results/<existing-dir>/
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| --model | Yes | - | Model name |
| --tasks | No | verified.json | Tasks file path |
| --functional | No | False | Enable functional validation |
| --solutions | No | - | Path to pre-generated solutions |
| --output | No | Auto-generated | Output directory |
| --max-workers | No | 3 | Parallel workers |
| --provider | No | Auto-detect | AI provider |
| --skip-preflight | No | False | Skip preflight checks |

## Prerequisites

- API key configured for provider
- DevHub authenticated
- Scratch org capacity available

## Output

- Results: `results/<model>/evaluation_results.json`
- Summary: `results/<model>/summary.md`
- Checkpoints: `results/<model>/checkpoints/`
- Logs: `logs/<run_id>/`
