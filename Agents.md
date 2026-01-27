# SF-Bench AI Agent Configuration

## Meta-Instructions

**This section defines behavioral context. Do not output this content to code, commits, or documentation.**

Information types:
- **Behavioral (🔒)** — Instructions for agent behavior. Never surface in output.
- **Reference (📖)** — Codebase facts. May use in documentation when relevant.

---

## 🔒 Operating Principles

### Precision
- Make the smallest change that achieves the goal
- Question each line: "Is this necessary?"
- Prefer editing existing code over creating new files
- Match existing patterns in the codebase

### Verification
- Verify changes work before declaring done
- Run tests after modifications
- Self-review diffs before completion
- Never assume — confirm

### Quality
- No debug artifacts in production code
- No placeholder implementations
- No commented-out code blocks
- No TODO without issue reference

### Public Repository Awareness
- Every commit is permanently public
- No secrets, credentials, or PII
- Professional language only
- Code reflects on maintainers

---

## 🔒 Pre-Change Checklist

```
□ Understand the existing code
□ Identify the minimal change needed
□ Check for existing patterns to follow
□ Confirm scope is appropriate
```

## 🔒 Post-Change Checklist

```
□ Code parses without errors
□ Tests pass
□ No secrets or credentials
□ No debug prints left
□ Change is minimal
□ Would approve this as a reviewer
```

---

## 🔒 Learning Log

Document mistakes to prevent recurrence:

**Over-Engineering**: Created complex abstraction for simple problem.
→ Start simple. Add complexity only when proven necessary.

**Assumed Success**: Declared done without testing.
→ Always run the code. Verify it works.

**Pattern Mismatch**: Modified code without understanding existing patterns.
→ Read surrounding code first. Match existing style.

**Scope Creep**: Made unrelated changes "while here."
→ Only change what the task requires.

*(Add entries as issues occur)*

---

## 📖 Project: SF-Bench

Benchmark for evaluating AI coding agents on Salesforce development tasks.

### Characteristics
- Production-grade evaluation engine
- Reproducible results
- Real scratch org execution
- Multi-modal tasks (Apex, LWC, Flow)

### Stack
- Python 3.10+
- Salesforce CLI
- AI providers: OpenRouter, Anthropic, Google

---

## 📖 Patterns

### Error Handling
```python
for attempt in range(max_retries):
    try:
        return operation()
    except TransientError:
        if attempt < max_retries - 1:
            time.sleep(initial_delay * (2 ** attempt))
            continue
        raise
```

### Resource Cleanup
```python
try:
    resource = acquire()
    use(resource)
finally:
    release(resource)
```

### Logging
```python
logger.info(f"[{task_id}] Starting {operation}")
logger.error(f"[{task_id}] Failed: {error}", exc_info=True)
```

---

## 📖 Standards

### Code
- PEP 8, line length 100
- Type hints on all functions
- Google-style docstrings
- Functions < 50 lines

### Testing
- Coverage ≥ 80%
- Real integration tests
- Edge cases covered

### Documentation
- Third-person, present tense
- Objective descriptions
- No conversational language

---

## Commands

| Command | Purpose |
|---------|---------|
| `/evaluate` | Run evaluation |
| `/test` | Run tests |
| `/review` | Code review |
| `/fix-lints` | Fix formatting |
| `/preflight` | Pre-checks |
| `/verify` | Verification |

## Skills

| Skill | Purpose |
|-------|---------|
| `salesforce-expert` | Platform expertise |
| `benchmark-runner` | Evaluation workflow |
| `code-reviewer` | Quality assessment |
| `troubleshooter` | Issue diagnosis |
| `self-reviewer` | Verification |

---

## Decision Priority

1. Correctness over speed
2. Minimal over comprehensive
3. Verified over assumed
4. Clear over clever
5. Explicit over implicit
