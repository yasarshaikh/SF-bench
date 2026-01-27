# Update Memory

Update memory bank files to reflect current project state.

## Steps

1. Review current work state
2. Update `activeContext.md` with current focus
3. Update `progress.md` with completed work and todos
4. Verify consistency across memory bank files

## Files to Update

### activeContext.md
- Current work focus
- Recent changes (with dates)
- Next steps
- Active decisions
- Blockers

### progress.md
- Completed features
- In-progress items
- Todos with priorities
- Known issues
- Recent achievements

## Update Triggers

Run this command after:
- Completing a feature
- Significant code changes (3+ files)
- Encountering or resolving blockers
- Changing priorities

## Format

### Recent Changes Entry
```markdown
- [YYYY-MM-DD] Brief description of what was completed
```

### Todo Entry
```markdown
- [ ] Task description - [Priority: High/Medium/Low]
```

### Completed Feature Entry
```markdown
- [Feature Name] - [Date] - Brief description
```

## Verification

After update:
1. Dates are current
2. Status reflects actual state
3. No stale information
4. Cross-references are valid
