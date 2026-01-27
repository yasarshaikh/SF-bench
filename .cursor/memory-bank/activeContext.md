# Active Context

## Current Work Focus

Running GPT-5 evaluation on lite tasks via RouteLLM.

## Recent Changes

- [2026-01-27] Pushed AI-native infrastructure to main (commit 121f303)
- [2026-01-27] Cleaned up ~3.5MB of generated/temporary files
- [2026-01-27] Fixed patch format issue: improved system prompt with concrete example
- [2026-01-27] Added _normalize_patch_headers() to ai_agent.py
- [2026-01-27] Added _pre_normalize_patch() to git.py
- [2026-01-27] Tested Grok (malformed patches) vs GPT-5 (correct format)
- [2026-01-27] GPT-5 evaluation running on lite.json tasks

## Next Steps

1. Review GPT-5 evaluation results
2. Commit patch format improvements
3. Run more comprehensive evaluations

## Active Decisions

- Using subagents for parallel work
- GPT-5 produces better formatted patches than Grok-4.1-fast
- Patch normalization added as safety net

## Blockers

- Grok model produces malformed patches (model limitation, not tool issue)

---

*Last update: 2026-01-27*
