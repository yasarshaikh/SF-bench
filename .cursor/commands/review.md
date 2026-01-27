# Review

Perform code review following SF-Bench quality standards.

## Checklist

### Critical (Must Fix)
- [ ] Error handling with retry logic
- [ ] Resource cleanup in finally blocks
- [ ] No hardcoded secrets
- [ ] Errors logged with context

### Important (Should Fix)
- [ ] PEP 8 compliance
- [ ] Type hints on all functions
- [ ] Google-style docstrings
- [ ] Test coverage ≥80%

### Suggestions
- [ ] Performance optimizations
- [ ] Documentation improvements
- [ ] Code simplification

## Review Steps

1. Understand the change (scope, intent)
2. Check critical issues first
3. Review code quality
4. Validate functionality
5. Provide prioritized feedback

## Feedback Format

```
**[CRITICAL]** Line XX
Issue: [Description]
Suggestion: [Fix]

**[IMPORTANT]** Line YY
Issue: [Description]
Suggestion: [Fix]
```

## Standards References

- `.cursor/rules/code_documentation.mdc`
- `.cursor/rules/technical_writing.mdc`
- `AGENTS.md` (error handling, logging patterns)
