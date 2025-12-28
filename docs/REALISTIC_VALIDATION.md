# SF-Bench Validation Methodology

## Our Role: Auditors, Not Predictors

SF-Bench is a **measurement tool**. We don't predict or claim what AI models "should" score. We:

- ✅ **Measure** actual performance
- ✅ **Report** objective results
- ✅ **Verify** functional outcomes
- ❌ ~~Predict expected success rates~~
- ❌ ~~Claim what models should achieve~~

---

## The Problem with Most AI Benchmarks

Most AI coding benchmarks check:
- ✅ Code compiles
- ✅ Unit tests pass
- ❌ **Does it actually work in production?**

This is like checking if a car starts, not if it can drive.

---

## SF-Bench's Approach: Outcome-Based Validation

We don't just check if the solution deploys. We verify the **business outcome is achieved**.

### Example: Flow Automation

**Task:** Create a Flow that creates a Task when Account.Type changes to 'Customer - Direct'

**Standard Benchmark (Inadequate):**
```bash
sf project deploy start --dry-run  # ✅ Deploys? Great! PASS
```

**SF-Bench Validation:**
```bash
# Step 1: Deploy Flow
sf project deploy start  # ✅ Deployed

# Step 2: Create test data that should trigger the Flow
sf apex run -c "
  Account acc = new Account(Name='Test', Type='Prospect');
  insert acc;
  acc.Type = 'Customer - Direct';
  update acc;
"

# Step 3: VERIFY THE OUTCOME
sf data query -q "SELECT Id, Subject FROM Task WHERE WhatId = :accId"

# Result: 1 Task with Subject containing 'Test' → PASS
# Result: 0 Tasks → FAIL (Flow didn't fire)
# Result: Wrong Subject → FAIL (Logic error)
```

---

## Validation Levels

| Level | Weight | What We Measure |
|-------|:------:|-----------------|
| Syntax | 10% | Code parses, valid XML/JSON |
| Deployment | 20% | Deploys to scratch org |
| Unit Tests | 20% | All tests pass, coverage ≥80% |
| **Functional** | **40%** | **Business outcome achieved** |
| Bulk Operations | 10% | Handles 200+ records |

**Total: 100 points**

---

## What We Measure

For each task, we measure:

1. **Did the solution deploy?** (Binary: Yes/No)
2. **Did unit tests pass?** (Ratio: X/Y passed)
3. **Did the functional test pass?** (Binary: Yes/No)
4. **Did bulk operations succeed?** (Binary: Yes/No)
5. **Any errors or timeouts?** (Logged)

We report these **as-is**, without interpretation or prediction.

---

## Task Structure

```json
{
  "instance_id": "flow-account-automation-001",
  "task_type": "FLOW",
  "problem_description": "...",
  
  "validation": {
    "command": "sf project deploy start",
    "expected_outcome": "Succeeded"
  },
  
  "functional_validation": {
    "description": "Verify Flow creates Task when Account type changes",
    "trigger_test_script": "scripts/flow/trigger_test.apex",
    "outcome_verifications": [
      {
        "name": "Verify Task Created",
        "query": "SELECT Id, Subject FROM Task WHERE WhatId = :accountId",
        "expected": {
          "record_count": 1,
          "field_value": { "field": "Subject", "contains": "Welcome" }
        }
      }
    ],
    "bulk_test_script": "scripts/flow/bulk_test.apex",
    "negative_test_script": "scripts/flow/should_not_trigger.apex"
  },
  
  "metadata": {
    "difficulty": "hard",
    "category": "flow",
    "validation_level": "functional"
  }
}
```

---

## How Results Are Reported

When a model is evaluated, we report:

```
Model: claude-3.5-sonnet
Tasks: 12
Passed: 8
Failed: 4
Pass Rate: 66.7%

Breakdown by Category:
- Apex: 2/2 (100%)
- LWC: 2/2 (100%)
- Flow: 1/2 (50%)
- Lightning Pages: 0/1 (0%)
- Architecture: 3/5 (60%)
```

**We don't say "this is good" or "this is bad"**. We report what we measured.

---

## For Contributors

When adding new tasks, include:

1. **Functional validation section** - How to verify the outcome
2. **Test scripts** - Apex scripts to create test data
3. **Outcome queries** - SOQL to verify results
4. **Negative tests** - What should NOT happen
5. **Bulk tests** - 200 record scenarios

---

## Credibility Principle

> **"When SF-Bench reports 75%, it means 75% of solutions passed all validation steps."**

We don't interpret. We don't predict. We measure and report.

---

*"A benchmark is only as credible as its objectivity."*
