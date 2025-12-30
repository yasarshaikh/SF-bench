"""
Task Schema Validation

Validates task JSON files against SF-Bench schema.
Inspired by SWE-bench's validation approach.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    value: Any = None


class TaskValidator:
    """Validates task definitions against SF-Bench schema."""
    
    REQUIRED_FIELDS = [
        "instance_id",
        "task_type",
        "repo_url",
        "base_commit",
        "problem_description",
        "validation",
    ]
    
    REQUIRED_VALIDATION_FIELDS = [
        "command",
        "expected_outcome",
    ]
    
    VALID_TASK_TYPES = [
        "APEX",
        "LWC",
        "FLOW",
        "LIGHTNING_PAGE",
        "PAGE_LAYOUT",
        "COMMUNITY",
        "EXPERIENCE",
        "ARCHITECTURE",
        "DEPLOY",
        "AGENTFORCE",
    ]
    
    def validate_task(self, task: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate a single task definition.
        
        Args:
            task: Task dictionary to validate
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in task:
                errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing"
                ))
        
        # Validate task_type
        if "task_type" in task:
            if task["task_type"] not in self.VALID_TASK_TYPES:
                errors.append(ValidationError(
                    field="task_type",
                    message=f"Invalid task_type '{task['task_type']}'. Must be one of: {', '.join(self.VALID_TASK_TYPES)}",
                    value=task["task_type"]
                ))
        
        # Validate validation object
        if "validation" in task:
            validation = task["validation"]
            if not isinstance(validation, dict):
                errors.append(ValidationError(
                    field="validation",
                    message="'validation' must be an object"
                ))
            else:
                for field in self.REQUIRED_VALIDATION_FIELDS:
                    if field not in validation:
                        errors.append(ValidationError(
                            field=f"validation.{field}",
                            message=f"Required validation field '{field}' is missing"
                        ))
        
        # Validate instance_id format
        if "instance_id" in task:
            instance_id = task["instance_id"]
            if not isinstance(instance_id, str) or len(instance_id) == 0:
                errors.append(ValidationError(
                    field="instance_id",
                    message="'instance_id' must be a non-empty string"
                ))
            elif not instance_id.replace("-", "").replace("_", "").isalnum():
                errors.append(ValidationError(
                    field="instance_id",
                    message="'instance_id' should contain only alphanumeric characters, hyphens, and underscores"
                ))
        
        # Validate repo_url
        if "repo_url" in task:
            repo_url = task["repo_url"]
            if not isinstance(repo_url, str):
                errors.append(ValidationError(
                    field="repo_url",
                    message="'repo_url' must be a string"
                ))
            elif not (repo_url.startswith("http://") or repo_url.startswith("https://")):
                errors.append(ValidationError(
                    field="repo_url",
                    message="'repo_url' must be a valid HTTP/HTTPS URL"
                ))
        
        # Validate timeouts (if present)
        if "timeouts" in task:
            timeouts = task["timeouts"]
            if not isinstance(timeouts, dict):
                errors.append(ValidationError(
                    field="timeouts",
                    message="'timeouts' must be an object"
                ))
            else:
                for timeout_type in ["setup", "run"]:
                    if timeout_type in timeouts:
                        timeout_value = timeouts[timeout_type]
                        if not isinstance(timeout_value, (int, float)) or timeout_value <= 0:
                            errors.append(ValidationError(
                                field=f"timeouts.{timeout_type}",
                                message=f"'{timeout_type}' timeout must be a positive number"
                            ))
        
        return errors
    
    def validate_task_file(self, file_path: Path) -> tuple[bool, List[ValidationError]]:
        """
        Validate a task JSON file.
        
        Args:
            file_path: Path to task JSON file
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check file exists
        if not file_path.exists():
            errors.append(ValidationError(
                field="file",
                message=f"File not found: {file_path}"
            ))
            return False, errors
        
        # Try to parse JSON
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(ValidationError(
                field="json",
                message=f"Invalid JSON: {str(e)}"
            ))
            return False, errors
        except Exception as e:
            errors.append(ValidationError(
                field="file",
                message=f"Error reading file: {str(e)}"
            ))
            return False, errors
        
        # Check if it's a list
        if not isinstance(data, list):
            errors.append(ValidationError(
                field="root",
                message="Task file must contain a JSON array"
            ))
            return False, errors
        
        # Validate each task
        for idx, task in enumerate(data):
            task_errors = self.validate_task(task)
            for error in task_errors:
                error.field = f"tasks[{idx}].{error.field}"
                errors.append(error)
        
        return len(errors) == 0, errors
    
    def print_errors(self, errors: List[ValidationError]):
        """Print validation errors in a readable format."""
        if not errors:
            print("✅ All tasks are valid!")
            return
        
        print(f"❌ Found {len(errors)} validation error(s):\n")
        for error in errors:
            print(f"  • {error.field}: {error.message}")
            if error.value is not None:
                print(f"    Value: {error.value}")


def validate_tasks_file(file_path: Path) -> bool:
    """
    Convenience function to validate a task file.
    
    Args:
        file_path: Path to task JSON file
    
    Returns:
        True if valid, False otherwise
    """
    validator = TaskValidator()
    is_valid, errors = validator.validate_task_file(file_path)
    
    if not is_valid:
        validator.print_errors(errors)
    
    return is_valid


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m sfbench.utils.task_validator <task_file.json>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    is_valid = validate_tasks_file(file_path)
    sys.exit(0 if is_valid else 1)
