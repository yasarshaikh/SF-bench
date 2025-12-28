# SF-Bench Realistic Validation

## The Problem with Current AI Benchmarks

Most AI coding benchmarks check:
- ✅ Code compiles
- ✅ Unit tests pass
- ❌ **Does it actually work?**

This is like checking if a car starts, not if it can drive.

---

## SF-Bench's Approach: Outcome-Based Validation

We don't just check if the solution deploys. We verify the **business outcome is achieved**.

### Example: Flow Automation

**Task:** Create a Flow that creates a Task when Account.Type changes to 'Customer - Direct'

**Old Validation (Inadequate):**
```bash
sf project deploy start --dry-run  # ✅ Deploys? Great! PASS
```

**SF-Bench Validation (Realistic):**
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

# Expected: 1 Task with Subject containing 'Test'
# If 0 Tasks → FAIL (Flow didn't fire or Task not created)
# If Subject wrong → FAIL (Logic error)
# If 1 Task with correct Subject → PASS
```

---

## Expected AI Success Rates (Realistic)

Based on real-world Salesforce development experience:

| Task Type | Current AI Success (One-Shot) | Notes |
|-----------|:-----------------------------:|-------|
| **Apex Trigger** | 70-80% | Usually works, may need tweaks |
| **Apex Integration** | 50-60% | Auth/retry logic often wrong |
| **LWC Component** | 60-70% | Error handling often incomplete |
| **LWC with Apex** | 50-60% | Wire/imperative patterns tricky |
| **Flow (Simple)** | 40-50% | Entry conditions often wrong |
| **Flow (Complex)** | 10-20% | Subflows, bulkification fail |
| **Lightning Page** | 20-30% | Visibility rules complex |
| **Page Layout** | 30-40% | XML structure finicky |
| **Experience Cloud** | 10-20% | Guest access, security complex |
| **Architecture** | 20-30% | Multi-component coordination hard |

**These are the numbers we expect to see in a realistic benchmark.**

If an AI scores 90%+ on Flows, either:
1. The tasks are too easy, OR
2. The validation is not realistic

---

## Validation Levels

### Level 1: Syntax (10 points)
- Code parses
- Valid XML/JSON
- No missing dependencies

### Level 2: Deployment (20 points)
- Deploys to scratch org
- No metadata errors
- All components recognized

### Level 3: Unit Tests (20 points)
- All tests pass
- Coverage >= 80%
- No test-specific hacks

### Level 4: Functional Tests (40 points) ⭐ **THE CORE**
- Create real test data
- Execute the solution
- Query database for results
- Verify expected outcomes

### Level 5: Production-Ready (10 points)
- Handles 200+ records
- No governor limit issues
- Proper error handling

**Total: 100 points**

---

## Task Structure for Realistic Validation

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
          "field_value": {
            "field": "Subject",
            "contains": "Welcome"
          }
        }
      }
    ],
    
    "bulk_test_script": "scripts/flow/bulk_test.apex",
    "negative_test_script": "scripts/flow/should_not_trigger.apex"
  },
  
  "metadata": {
    "expected_ai_success_rate": "30%",
    "validation_level": "functional"
  }
}
```

---

## Why This Matters for Credibility

When someone uses SF-Bench results to evaluate an AI model:

**If we say:** "Model X scores 75% on Flows"

**It should mean:** "75% of Model X's Flow solutions work correctly the first time, no tweaks needed"

**NOT:** "75% of Model X's Flow solutions deploy without errors (but only 30% actually work)"

---

## Implementation Status

| Component | Status | Notes |
|-----------|:------:|-------|
| FunctionalValidator class | ✅ Created | Core validation logic |
| Task schema with functional_validation | ✅ Created | realistic.json |
| Test scripts for each task | 🚧 In Progress | Need Apex scripts |
| Integration with evaluate.py | 🚧 Pending | Need to wire up |
| End-to-end testing | 🚧 Pending | Need scratch org |

---

## For Contributors

When adding new tasks, ALWAYS include:

1. **functional_validation** section
2. **Test scripts** that create real data
3. **Outcome queries** that verify results
4. **Negative tests** (what should NOT happen)
5. **Bulk tests** (200 records)
6. **expected_ai_success_rate** (be realistic!)

A task without functional validation is an **incomplete task**.

---

*"A benchmark is only as credible as its worst validation."*
