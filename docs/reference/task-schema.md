---
layout: default
title: Task Schema Reference - SF-Bench Task Format
description: Complete reference for SF-Bench task JSON schema. Learn how to create and validate tasks for Apex, LWC, Flow, and other Salesforce development scenarios.
keywords: sf-bench task schema, task format, task json specification, salesforce benchmark task format, ai benchmark task definition
---

# Task Schema Reference

Complete reference for SF-Bench task JSON format.

---

## Schema Version

**Current Version:** 1.0  
**Format:** JSON array of task objects

---

## Top-Level Structure

```json
[
  {
    "instance_id": "apex-trigger-handler-001",
    "task_type": "APEX",
    "repo_url": "https://github.com/trailheadapps/apex-recipes",
    "base_commit": "main",
    "problem_description": "...",
    "validation": {...},
    "timeouts": {...},
    "metadata": {...}
  }
]
```

---

## Required Fields

### `instance_id` (string, required)
Unique identifier for the task.
- Format: `<category>-<subcategory>-<number>`
- Examples: `"apex-trigger-handler-001"`, `"lwc-component-001"`
- Must be alphanumeric with hyphens/underscores only

### `task_type` (string, required)
Type of Salesforce development task.
- Valid values: `APEX`, `LWC`, `FLOW`, `LIGHTNING_PAGE`, `PAGE_LAYOUT`, `COMMUNITY`, `EXPERIENCE`, `ARCHITECTURE`, `DEPLOY`, `AGENTFORCE`

### `repo_url` (string, required)
GitHub repository URL containing the codebase.
- Must be a valid HTTP/HTTPS URL
- Example: `"https://github.com/trailheadapps/apex-recipes"`

### `base_commit` (string, required)
Git commit hash or branch name to checkout.
- Examples: `"main"`, `"abc123def456"`

### `problem_description` (string, required)
Detailed description of the task/problem to solve.
- Should be clear and specific
- Include requirements and constraints

### `validation` (object, required)
Validation configuration for the task.

```json
{
  "command": "sf apex run test --class-names AccountTriggerHandlerTests --result-format json",
  "expected_outcome": "Passed",
  "code_checks": [
    "null_check_required",
    "no_hardcoded_ids"
  ]
}
```

**Fields:**
- `command` (string, required): Command to run for validation
- `expected_outcome` (string, required): Expected result (e.g., "Passed", "Succeeded")
- `code_checks` (array, optional): List of code quality checks

---

## Optional Fields

### `timeouts` (object, optional)
Timeout configuration in seconds.

```json
{
  "setup": 600,
  "run": 300
}
```

**Fields:**
- `setup` (number, optional): Timeout for setup phase (default: 600)
- `run` (number, optional): Timeout for execution phase (default: 300)

### `metadata` (object, optional)
Additional metadata about the task.

```json
{
  "difficulty": "medium",
  "category": "apex",
  "subcategory": "trigger-handling",
  "verified_repo": true,
  "repo_stars": 1059,
  "file_path": "force-app/main/default/classes/Trigger Recipes/AccountTriggerHandler.cls"
}
```

**Fields:**
- `difficulty` (string, optional): Task difficulty (`easy`, `medium`, `hard`, `expert`)
- `category` (string, optional): Task category
- `subcategory` (string, optional): Task subcategory
- `verified_repo` (boolean, optional): Whether repo is verified
- `repo_stars` (number, optional): GitHub stars count
- `file_path` (string, optional): Primary file path for the task

---

## Complete Example

```json
{
  "instance_id": "apex-trigger-handler-001",
  "task_type": "APEX",
  "repo_url": "https://github.com/trailheadapps/apex-recipes",
  "base_commit": "main",
  "problem_description": "The AccountTriggerHandler class has a potential NullPointerException when Account.Owner is null. Implement proper null-safety checks in the handler methods without breaking existing test coverage.",
  "validation": {
    "command": "sf apex run test --class-names AccountTriggerHandlerTests --result-format json",
    "expected_outcome": "Passed",
    "code_checks": [
      "null_check_required",
      "no_hardcoded_ids",
      "maintains_test_coverage"
    ]
  },
  "timeouts": {
    "setup": 600,
    "run": 300
  },
  "metadata": {
    "difficulty": "medium",
    "category": "apex",
    "subcategory": "trigger-handling",
    "verified_repo": true,
    "repo_stars": 1059,
    "file_path": "force-app/main/default/classes/Trigger Recipes/AccountTriggerHandler.cls"
  }
}
```

---

## Validation

Validate task files using the task validator:

```bash
# Validate a task file
python -m sfbench.utils.task_validator data/tasks/verified.json

# Or use in Python
from sfbench.utils.task_validator import validate_tasks_file
from pathlib import Path

is_valid = validate_tasks_file(Path("data/tasks/verified.json"))
```

---

## Task Types

### APEX
Apex classes, triggers, and test classes.

### LWC
Lightning Web Components (JavaScript/HTML/CSS).

### FLOW
Salesforce Flows (Screen Flows, Record-Triggered Flows, etc.).

### LIGHTNING_PAGE
Lightning Page configurations (FlexiPages).

### PAGE_LAYOUT
Page Layout metadata.

### COMMUNITY
Experience Cloud (Community) sites.

### EXPERIENCE
Experience Cloud customization.

### ARCHITECTURE
Full-stack architecture tasks (multiple components).

### DEPLOY
Deployment and metadata management tasks.

### AGENTFORCE
Agentforce script recipes.

---

## Best Practices

1. **Clear Problem Description**: Be specific about requirements
2. **Realistic Tasks**: Use real-world scenarios
3. **Proper Validation**: Ensure validation commands are correct
4. **Appropriate Timeouts**: Set timeouts based on task complexity
5. **Complete Metadata**: Include all relevant metadata for categorization

---

## Related Documentation

- [Evaluation Guide](../guides/evaluation.html)
- [Result Schema](result-schema.html)
- [Contributing Guide](https://github.com/yasarshaikh/SF-bench/blob/main/CONTRIBUTING.md)

---

*Last updated: December 2025*
