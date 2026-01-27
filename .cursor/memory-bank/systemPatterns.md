# System Patterns: SF-Bench

## Architecture Overview

SF-Bench follows a pipeline architecture with modular components:

```
┌─────────────┐    ┌──────────────┐    ┌────────────┐    ┌───────────┐
│  Preflight  │ → │  Solution    │ → │  Task      │ → │ Reporting │
│  Checks     │    │  Generation  │    │  Execution │    │ & Scoring │
└─────────────┘    └──────────────┘    └────────────┘    └───────────┘
```

## Core Components

### BenchmarkEngine (`sfbench/engine.py`)

The orchestrator component manages the complete evaluation lifecycle:
- Task loading and validation
- Runner instantiation via factory pattern
- Parallel or sequential task execution
- Result aggregation and checkpoint management

### Runner Pattern (`sfbench/runners/`)

Task-specific runners inherit from `BaseRunner`:
- `ApexRunner`: Apex class, trigger, and test execution
- `LWCRunner`: Lightning Web Component deployment and validation
- `FlowRunner`: Flow automation deployment and execution
- `ArchitectureRunner`: Cross-cutting architectural tasks
- `DeployRunner`: Deployment-only validation tasks

Each runner implements:
```python
def setup() -> bool        # Prepare scratch org and repo
def deploy() -> bool       # Deploy code to scratch org
def validate() -> bool     # Run tests and validation
def cleanup()             # Resource cleanup (finally block)
```

### Validation Pipeline

Three-stage validation ensures production-readiness:
1. **Deployment Validation**: Code deploys without errors
2. **Test Validation**: Unit tests pass with ≥80% coverage
3. **Functional Validation**: Business outcomes verified via execution

### Checkpoint System (`sfbench/utils/checkpoint.py`)

Supports long-running evaluation recovery:
- Creates checkpoints after each task completion
- Stores task results, metadata, and configuration hash
- Enables resume from latest checkpoint on failure
- Verifies checkpoint integrity via SHA-256 hash

## Design Patterns

### Retry with Exponential Backoff

All transient operations use retry logic:
```python
for attempt in range(max_retries):
    try:
        result = operation()
        return result
    except TransientError:
        if attempt < max_retries - 1:
            delay = initial_delay * (2 ** attempt)
            time.sleep(delay)
            continue
        raise
```

Applied to:
- Scratch org creation (3 attempts: 2s, 4s, 8s)
- API calls to AI providers
- Salesforce CLI operations

### Multi-Strategy Fallback

Patch application uses 4 fallback strategies:
1. **Strict**: Standard `git apply`
2. **Reject**: Apply with reject files for conflicts
3. **3-way**: Three-way merge for complex patches
4. **Fuzzy**: Fuzzy matching for context variations

### Resource Cleanup Pattern

All scratch org operations use finally-block cleanup:
```python
try:
    org_alias = create_scratch_org()
    deploy_and_validate(org_alias)
finally:
    delete_scratch_org(org_alias)  # Always executes
```

### Structured Logging

All operations log with context:
```python
logger.info(f"Deploying task {task_id} to {org_alias}")
logger.debug(f"Patch preview: {patch[:500]}...")
logger.error(f"Deployment failed: {error}", exc_info=True)
```

## Data Flow

```
Task JSON → TaskValidator → BenchmarkEngine → RunnerFactory
                                    ↓
                              Task Runner
                                    ↓
                          ┌─────────────────┐
                          │ Scratch Org Ops │
                          │ - create_org    │
                          │ - deploy_code   │
                          │ - run_tests     │
                          │ - delete_org    │
                          └─────────────────┘
                                    ↓
                              TestResult
                                    ↓
                          ResultConverter → Schema v2 JSON
```

## Integration Points

### Salesforce CLI Integration (`sfbench/utils/sfdx.py`)
- Org creation and deletion
- Metadata deployment
- Test execution
- Anonymous Apex execution

### AI Provider Integration (`sfbench/utils/ai_agent.py`)
- Solution generation via LLM API
- Provider abstraction (OpenRouter, Anthropic, Google, etc.)
- Format validation for git diff patches

### Git Integration (`sfbench/utils/git.py`)
- Repository cloning and management
- Patch application with fallback strategies
- Status verification for "no manual tweaks" check
