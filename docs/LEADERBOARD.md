---
layout: default
title: SF-Bench Leaderboard - AI Model Rankings | Salesforce AI Benchmark Results
description: Current Salesforce AI benchmark results and rankings for AI coding agents. View performance rankings for Apex, LWC, Flow, and Lightning development tasks.
keywords: salesforce benchmark leaderboard, ai model rankings, salesforce ai performance, llm benchmark results, salesforce ai benchmark leaderboard, sf benchmark results
---

# SF-Bench Leaderboard

*Last updated: 2025-12-30 UTC*

> **Status**: SF-Bench is now running full evaluations with functional validation and weighted scoring (0-100 points). Results show realistic performance with functional validation enabled.

## Overall Rankings

| Rank | Model | Overall | Functional Score | LWC | Deploy | Apex | Flow | Lightning Pages | Experience Cloud | Architecture |
|:----:|-------|:-------:|:----------------:|:---:|:------:|:----:|:----:|:---------------:|:----------------:|:------------:|
| 🥇 | **Claude Sonnet 4.5** | **41.67%** | **6.0%** | 100% | 100% | 100% | 0%* | 0% | 0% | 0% |
| 🥈 | **Gemini 2.5 Flash** | **25.0%** | - | 100% | 100% | 0%* | 0%* | 0% | 0% | 0% |
| - | *More results pending* | -% | - | -% | -% | -% | -% | -% | -% | -% |

*\* Apex and Flow tasks failed due to scratch org creation issues (being fixed)*

### Known Issues

**Claude Opus 4.5 (RouteLLM) - 2025-12-29**: 0% pass rate - All tasks failed due to patch application issues. This evaluation was completed with the previous patch application system. Re-evaluation recommended with improved patch handling.

**Grok 4.1 Fast (RouteLLM) - 2025-12-30**: Evaluation completed. Errors were due to error handling bugs (org creation warning parsing, malformed patch cleaning) which have been fixed. Re-evaluation recommended.

> **Note**: Functional Score (0-100) is calculated using weighted validation: Deploy(10%) + Unit Tests(20%) + Functional(50%) + Bulk(10%) + No Tweaks(10%). See [VALIDATION_METHODOLOGY.md](./VALIDATION_METHODOLOGY.html) for details.

## Detailed Results

### Gemini 2.5 Flash (Run: 2025-12-28)

| Segment | Tasks | Passed | Pass Rate | Notes |
|---------|:-----:|:------:|:---------:|-------|
| **LWC** | 2 | 2 | ✅ 100% | Jest tests passed (local validation) |
| **Deploy** | 1 | 1 | ✅ 100% | Metadata deployment succeeded |
| Apex | 2 | 0 | ❌ 0% | Scratch org creation issues |
| Flow | 2 | 0 | ❌ 0% | Scratch org creation issues |
| Lightning Pages | 1 | 0 | ❌ 0% | Outcome validation failed |
| Page Layouts | 1 | 0 | ❌ 0% | Scratch org creation issues |
| Experience Cloud | 1 | 0 | ❌ 0% | Outcome validation failed |
| Architecture | 1 | 0 | ❌ 0% | Outcome validation failed |
| Agentforce | 1 | 0 | ❌ 0% | Scratch org creation issues |
| **Total** | **12** | **3** | **25.0%** | Deployment-only validation |

**Validation Mode**: Deployment-only (functional validation pending systematic testing)

### Claude Sonnet 4.5 (Run: 2025-12-28)

| Segment | Tasks | Passed | Pass Rate | Functional Score | Notes |
|---------|:-----:|:------:|:---------:|:----------------:|-------|
| **LWC** | 2 | 2 | ✅ 100% | 10.0% | Jest tests passed, bulk tests passed |
| **Deploy** | 1 | 1 | ✅ 100% | 10.0% | Metadata deployment succeeded |
| **Apex** | 2 | 2 | ✅ 100% | 0.0% | Deployment passed, functional tests failed |
| Flow | 2 | 0 | ❌ 0% | - | Scratch org creation failed |
| Lightning Pages | 1 | 0 | ❌ 0% | - | Outcome validation failed |
| Page Layouts | 1 | 0 | ❌ 0% | - | Deployment failed |
| Experience Cloud | 1 | 0 | ❌ 0% | - | Outcome validation failed |
| Architecture | 1 | 0 | ❌ 0% | - | Outcome validation failed |
| Agentforce | 1 | 0 | ❌ 0% | - | Outcome validation failed |
| **Total** | **12** | **5** | **41.67%** | **6.0%** | **Functional validation enabled** |

**Validation Mode**: Functional validation with weighted scoring (0-100 points)
**Average Functional Score**: 6.0% (out of 100)
- Deploy: 10% ✅
- Unit Tests: 20% ❌
- Functional: 50% ❌ (core requirement)
- Bulk: 10% ✅
- No Tweaks: 10% ❌

## Current Status

SF-Bench is now running full evaluations with functional validation:

1. ✅ **Atomic Testing**: Each component tested individually (completed)
2. ✅ **E2E Validation**: Single model, single task end-to-end test (completed)
3. ✅ **Full Evaluation**: Complete benchmark run with functional validation (completed)

### Recent Evaluations

**Grok 4.1 Fast (RouteLLM) - 2025-12-30**
- **Result**: 0% pass rate (0/12 tasks)
- **Issues**: 10 tasks failed due to org creation error parsing, 2 tasks failed due to malformed patch handling
- **Status**: Errors were due to error handling bugs (not model issues). Fixes implemented:
  - Improved org creation error parsing (filters CLI warnings)
  - Enhanced patch cleaning (handles malformed patches)
- **Note**: Re-evaluation recommended with improved error handling

**Claude Opus 4.5 (RouteLLM) - 2025-12-29**
- **Result**: 0% pass rate (0/12 tasks)
- **Issue**: Patch application failures with previous patch system
- **Status**: Re-evaluation recommended with improved multi-strategy patch application

## Evaluation Methodology

SF-Bench uses a **multi-level validation approach**:

1. **Syntax Validation**: Code compiles without errors
2. **Deployment Validation**: Metadata deploys successfully
3. **Unit Test Validation**: Apex unit tests pass
4. **Functional Validation**: Actual business outcomes verified (bulk operations, negative cases)
5. **Production-Ready**: Security, error handling, governor limits

See [VALIDATION_METHODOLOGY.md](./VALIDATION_METHODOLOGY.html) for details.

---

## How to Submit Results

1. Run SF-Bench on your model
2. [Submit results via issue](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)
3. Results will be verified and added to leaderboard

See [CONTRIBUTING.md](../CONTRIBUTING.html) for details.
