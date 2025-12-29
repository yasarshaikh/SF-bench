---
layout: default
title: Validation Methodology - How SF-Bench Validates AI Solutions
description: Comprehensive guide to SF-Bench validation methodology. Learn how we verify functional outcomes, not just deployment success, with weighted scoring and multi-level validation.
keywords: salesforce benchmark validation, functional validation, ai code validation, salesforce testing methodology
---

# SF-Bench Validation Methodology

## Core Philosophy

> **"If a benchmark says 100% pass rate, it must mean the solution works 100% of the time in production, first try."**

This is NOT just about:
- ❌ Code compiles
- ❌ Deployment succeeds
- ❌ Unit tests pass

This IS about:
- ✅ Business requirement is met
- ✅ Functionality works as intended
- ✅ Solution handles edge cases
- ✅ No manual tweaks needed

---

## Validation Levels

### Level 1: Syntax Validation (Necessary but NOT Sufficient)
- Code parses without errors
- Metadata XML is valid
- Dependencies are resolved

### Level 2: Deployment Validation (Still NOT Sufficient)
- Deploys to scratch org without errors
- All metadata types recognized
- No missing references

### Level 3: Functional Validation (REQUIRED for SF-Bench)
- Solution actually DOES what it's supposed to do
- Tested with real data in real org
- Outcome matches expected business result

### Level 4: Production-Ready Validation (IDEAL)
- Handles bulk data (200+ records)
- Error handling works correctly
- Performance is acceptable
- Security model is correct

---

## Validation by Task Type

### APEX - Trigger/Class Validation

**Current (Inadequate):**
```
sf apex run test --class-names MyTest
```

**Required (SF-Bench Standard):**
```yaml
validation:
  steps:
    - name: "Deploy to Scratch Org"
      command: "sf project deploy start"
      success_criteria: "exit_code == 0"
    
    - name: "Run Unit Tests"
      command: "sf apex run test --code-coverage --result-format json"
      success_criteria: 
        - "tests_passed == tests_total"
        - "code_coverage >= 80"
    
    - name: "Execute Trigger with Test Data"
      command: "sf apex run --file scripts/test_trigger.apex"
      # test_trigger.apex creates records that should fire the trigger
      
    - name: "Verify Outcome"
      command: "sf data query --query \"SELECT Id, Description FROM Account WHERE Name = 'Test Account'\""
      success_criteria: 
        - "Description CONTAINS 'Owner:'"  # Verify trigger actually ran
        - "Description NOT CONTAINS 'null'"  # Verify null-safety worked
    
    - name: "Verify No Governor Limit Issues"
      command: "sf apex run --file scripts/bulk_test.apex"  # Insert 200 records
      success_criteria: "exit_code == 0"
```

---

### LWC - Component Validation

**Current (Partially Adequate):**
```
npm run test:unit
```

**Required (SF-Bench Standard):**
```yaml
validation:
  steps:
    - name: "Run Jest Tests"
      command: "npm run test:unit -- --coverage"
      success_criteria: 
        - "tests_passed == tests_total"
        - "coverage >= 80"
    
    - name: "Deploy to Scratch Org"
      command: "sf project deploy start"
      success_criteria: "exit_code == 0"
    
    - name: "Verify Apex Controller Works"
      command: "sf apex run --file scripts/test_controller.apex"
      success_criteria: "output CONTAINS 'SUCCESS'"
    
    - name: "UI Smoke Test (via UTAM or Playwright)"
      command: "npm run test:e2e -- --spec apexImperativeMethod"
      success_criteria:
        - "component_renders == true"
        - "no_console_errors == true"
        - "loading_state_works == true"
        - "error_state_works == true"
```

---

### FLOW - Record-Triggered Flow Validation

**Current (Completely Inadequate):**
```
sf project deploy start --dry-run
```

**Required (SF-Bench Standard):**
```yaml
validation:
  steps:
    - name: "Deploy Flow"
      command: "sf project deploy start --source-dir force-app/main/default/flows"
      success_criteria: "exit_code == 0"
    
    - name: "Activate Flow"
      command: "sf apex run --file scripts/activate_flow.apex"
      success_criteria: "Flow.Status == 'Active'"
    
    - name: "Create Test Record (Trigger Conditions Met)"
      command: "sf apex run --file scripts/create_test_account.apex"
      # Creates Account with Type='Customer - Direct', AnnualRevenue=2000000
      
    - name: "Wait for Flow Execution"
      command: "sleep 5"  # Allow async processing
    
    - name: "Verify Task Created"
      query: "SELECT Id, Subject, WhatId, ActivityDate FROM Task WHERE WhatId = :accountId"
      success_criteria:
        - "record_count == 1"
        - "Subject CONTAINS 'High Value Account'"
        - "ActivityDate == TODAY() + 7"
    
    - name: "Verify Contacts Updated"
      query: "SELECT Id, Level__c FROM Contact WHERE AccountId = :accountId AND Title LIKE '%Director%'"
      success_criteria:
        - "Level__c == 'Primary' FOR ALL RECORDS"
    
    - name: "Verify Platform Event Published"
      command: "sf apex run --file scripts/check_platform_event.apex"
      success_criteria: "event_published == true"
    
    - name: "Test Bulk (200 records)"
      command: "sf apex run --file scripts/bulk_insert_accounts.apex"
      success_criteria:
        - "exit_code == 0"
        - "tasks_created == 200"
        - "no_flow_errors"
    
    - name: "Test Entry Condition NOT Met (Negative Test)"
      command: "sf apex run --file scripts/create_low_value_account.apex"
      success_criteria: "tasks_created == 0"  # Flow should NOT fire
```

---

### LIGHTNING PAGE - FlexiPage Validation

**Current (Inadequate):**
```
sf project deploy start --dry-run
```

**Required (SF-Bench Standard):**
```yaml
validation:
  steps:
    - name: "Deploy FlexiPage"
      command: "sf project deploy start --source-dir force-app/main/default/flexipages"
      success_criteria: "exit_code == 0"
    
    - name: "Assign to App/Record Type"
      command: "sf apex run --file scripts/assign_flexipage.apex"
      success_criteria: "assignment_success == true"
    
    - name: "Create Test Record"
      command: "sf data create record --sobject Property__c --values \"Name='Test Property' Status__c='Available'\""
    
    - name: "Capture Page Screenshot (or UTAM test)"
      command: "npm run test:e2e -- --spec propertyRecordPage"
      success_criteria:
        - "page_loads == true"
        - "field_sections_visible >= 4"
        - "action_bar_present == true"
    
    - name: "Test Visibility Rules"
      commands:
        - "sf data update record --sobject Property__c --record-id :id --values \"Status__c='Sold'\""
        - "npm run test:e2e -- --spec propertyRecordPage --status=Sold"
      success_criteria:
        - "sold_section_visible == true"
        - "available_section_hidden == true"
    
    - name: "Test Mobile Responsiveness"
      command: "npm run test:e2e -- --spec propertyRecordPage --viewport=mobile"
      success_criteria: "mobile_layout_correct == true"
```

---

### EXPERIENCE CLOUD - Site Validation

**Current (Inadequate):**
```
sf project deploy start --dry-run
```

**Required (SF-Bench Standard):**
```yaml
validation:
  steps:
    - name: "Deploy Site Configuration"
      command: "sf project deploy start --source-dir force-app/main/default/experiences"
      success_criteria: "exit_code == 0"
    
    - name: "Publish Site"
      command: "sf community publish --name E_Bikes1"
      success_criteria: "exit_code == 0"
    
    - name: "Wait for Publication"
      command: "sleep 30"  # Sites take time to publish
    
    - name: "Test Guest Access"
      command: "curl -s https://ebikes1.preview.salesforce-sites.com/"
      success_criteria:
        - "http_status == 200"
        - "response CONTAINS 'E-Bikes'"
    
    - name: "Test Authenticated Access"
      command: "npm run test:e2e -- --spec ebikesAuth --user=testuser"
      success_criteria:
        - "login_works == true"
        - "profile_page_loads == true"
        - "order_history_visible == true"
    
    - name: "Test Product Navigation"
      command: "npm run test:e2e -- --spec ebikesNavigation"
      success_criteria:
        - "category_navigation_works == true"
        - "product_detail_loads == true"
        - "add_to_cart_works == true"
    
    - name: "Test Mobile Responsiveness"
      command: "npm run test:e2e -- --spec ebikes --viewport=mobile"
      success_criteria: "mobile_navigation_works == true"
```

---

## Scoring Methodology

### Pass Criteria (Must meet ALL)

| Check | Weight | Meaning |
|-------|:------:|---------|
| Deploys Successfully | 10% | Necessary but not sufficient |
| Unit Tests Pass | 20% | Code quality check |
| Functional Test Pass | 50% | **Core requirement** |
| Bulk Test Pass | 10% | Production readiness |
| No Manual Tweaks | 10% | True one-shot solution |

### Score Interpretation

| Score | What It Means |
|:-----:|---------------|
| 100% | All validation steps passed |
| 80-99% | Most steps passed, minor issues |
| 50-79% | Partial success |
| 20-49% | Limited success |
| 0-19% | Most steps failed |

**We report scores objectively.** We don't claim what's "good" or "bad" - users decide based on their requirements.

---

## Implementation Approach

### Phase 1: Task Definition Enhancement
- Add `functional_validation` section to each task
- Define specific queries/commands to verify outcomes
- Include expected data values

### Phase 2: Test Data Setup
- Create Apex scripts for test data creation
- Include negative test cases
- Support bulk testing

### Phase 3: Validation Runner Enhancement
- Execute multi-step validation pipelines
- Capture detailed results at each step
- Calculate weighted scores

### Phase 4: Reporting
- Show step-by-step validation results
- Highlight where solutions fail
- Provide actionable feedback

---

## Why This Matters

When a model scores **75% on SF-Bench**, it should mean:
- 75% of solutions work **first try, no tweaks**
- 25% need some iteration

NOT:
- 75% of solutions deploy without errors
- But only 30% actually work

**This benchmark must reflect real-world developer experience.**

---

*"A benchmark is only as credible as its validation methodology."*
