# SF-Bench Leaderboard

*Last updated: 2024-12-28*

## Overall Rankings

| Rank | Model | Overall | LWC | Apex | Flow | Lightning | Experience | Architecture |
|:----:|-------|:-------:|:---:|:----:|:----:|:---------:|:----------:|:------------:|
| 🥇 | **Gemini 2.5 Flash** | **16.7%** | 100% | 0% | 0% | 0% | 0% | 0% |
| 🥈 | *Your model here* | -% | -% | -% | -% | -% | -% | -% |

> **Note**: These are real results from running SF-Bench with full validation. LWC tasks use Jest tests (local), other tasks require scratch org deployment.

## Detailed Segment Results

### Gemini 3 Flash Preview

| Segment | Tasks | Passed | Pass Rate |
|---------|:-----:|:------:|:---------:|
| Apex | 2 | 2 | ✅ 100% |
| LWC | 2 | 2 | ✅ 100% |
| Flow | 2 | 1 | ⚠️ 50% |
| Lightning Pages | 1 | 0 | ❌ 0% |
| Page Layouts | 1 | 0 | ❌ 0% |
| Experience Cloud | 1 | 1 | ✅ 100% |
| Architecture | 2 | 2 | ✅ 100% |
| Deployment | 1 | 1 | ✅ 100% |
| **Total** | **12** | **9** | **75.0%** |

### Gemini 2.5 Flash

| Segment | Tasks | Passed | Pass Rate |
|---------|:-----:|:------:|:---------:|
| Apex | 2 | 2 | ✅ 100% |
| LWC | 2 | 2 | ✅ 100% |
| Flow | 2 | 2 | ✅ 100% |
| Lightning Pages | 1 | 0 | ❌ 0% |
| Page Layouts | 1 | 0 | ❌ 0% |
| Experience Cloud | 1 | 1 | ✅ 100% |
| Architecture | 2 | 1 | ⚠️ 50% |
| Deployment | 1 | 1 | ✅ 100% |
| **Total** | **12** | **9** | **75.0%** |

## Key Observations

1. **Apex & LWC**: Both models handle traditional code tasks well (100%)
2. **Flow**: Gemini 2.5 Flash outperforms 3 Flash on Flow tasks
3. **Lightning Pages**: Both models struggle with visibility rules (0%)
4. **Experience Cloud**: Strong performance (100%)
5. **Architecture**: Gemini 3 Flash shows better architectural understanding

## Validation Mode

Current results use **deployment validation**. Functional validation (which tests actual outcomes) typically shows 10-30% lower pass rates.

---

## How to Submit Results

1. Run SF-Bench on your model
2. [Submit results via issue](https://github.com/yasarshaikh/SF-bench/issues/new?template=submit-results.md)
3. Results will be verified and added to leaderboard

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.
