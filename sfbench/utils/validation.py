"""
Task schema validation utilities.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sfbench import Task, TaskType


class TaskValidationError(Exception):
    """Raised when a task fails validation."""
    pass


class TaskValidator:
    """Validates task schemas and data."""
    
    REQUIRED_FIELDS = [
        'instance_id',
        'task_type',
        'repo_url',
        'base_commit',
        'problem_description',
        'validation',
        'timeouts'
    ]
    
    REQUIRED_VALIDATION_FIELDS = ['command', 'expected_outcome']
    REQUIRED_TIMEOUT_FIELDS = ['setup', 'run']
    
    VALID_TASK_TYPES = {t.value for t in TaskType}
    
    @classmethod
    def validate_task(cls, task_data: Dict[str, Any]) -> List[str]:
        """
        Validate a single task dictionary.
        
        Args:
            task_data: Task dictionary to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in task_data:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return errors  # Don't continue if required fields are missing
        
        # Validate task_type
        task_type = task_data.get('task_type')
        if task_type not in cls.VALID_TASK_TYPES:
            errors.append(
                f"Invalid task_type: {task_type}. "
                f"Must be one of: {', '.join(cls.VALID_TASK_TYPES)}"
            )
        
        # Validate validation config
        validation = task_data.get('validation', {})
        if not isinstance(validation, dict):
            errors.append("validation must be a dictionary")
        else:
            for field in cls.REQUIRED_VALIDATION_FIELDS:
                if field not in validation:
                    errors.append(f"Missing required validation field: {field}")
        
        # Validate timeouts
        timeouts = task_data.get('timeouts', {})
        if not isinstance(timeouts, dict):
            errors.append("timeouts must be a dictionary")
        else:
            for field in cls.REQUIRED_TIMEOUT_FIELDS:
                if field not in timeouts:
                    errors.append(f"Missing required timeout field: {field}")
                elif not isinstance(timeouts[field], int) or timeouts[field] <= 0:
                    errors.append(f"timeout.{field} must be a positive integer")
        
        # Validate instance_id format (should be non-empty string)
        instance_id = task_data.get('instance_id', '')
        if not instance_id or not isinstance(instance_id, str):
            errors.append("instance_id must be a non-empty string")
        
        # Validate repo_url format (should be a URL)
        repo_url = task_data.get('repo_url', '')
        if not repo_url or not isinstance(repo_url, str):
            errors.append("repo_url must be a non-empty string")
        elif not (repo_url.startswith('http://') or repo_url.startswith('https://') or repo_url.startswith('git@')):
            errors.append("repo_url should be a valid URL or git SSH URL")
        
        # Validate base_commit (should be non-empty string)
        base_commit = task_data.get('base_commit', '')
        if not base_commit or not isinstance(base_commit, str):
            errors.append("base_commit must be a non-empty string")
        
        return errors
    
    @classmethod
    def validate_tasks_file(cls, tasks_file: Path) -> tuple[List[Task], List[str]]:
        """
        Validate and load tasks from a JSON file.
        
        Args:
            tasks_file: Path to tasks JSON file
            
        Returns:
            Tuple of (valid_tasks, errors)
        """
        errors = []
        valid_tasks = []
        
        if not tasks_file.exists():
            return [], [f"Tasks file not found: {tasks_file}"]
        
        try:
            with open(tasks_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return [], [f"Invalid JSON in tasks file: {str(e)}"]
        except Exception as e:
            return [], [f"Failed to read tasks file: {str(e)}"]
        
        # Handle both single task and list of tasks
        if isinstance(data, dict):
            task_list = [data]
        elif isinstance(data, list):
            task_list = data
        else:
            return [], ["Tasks file must contain a JSON object or array"]
        
        # Validate each task
        for idx, task_data in enumerate(task_list):
            task_errors = cls.validate_task(task_data)
            
            if task_errors:
                task_id = task_data.get('instance_id', f'task[{idx}]')
                for error in task_errors:
                    errors.append(f"{task_id}: {error}")
            else:
                try:
                    task = Task.from_dict(task_data)
                    valid_tasks.append(task)
                except Exception as e:
                    task_id = task_data.get('instance_id', f'task[{idx}]')
                    errors.append(f"{task_id}: Failed to create Task object: {str(e)}")
        
        return valid_tasks, errors
    
    @classmethod
    def validate_and_load(cls, tasks_file: Path) -> List[Task]:
        """
        Validate and load tasks, raising an exception if validation fails.
        
        Args:
            tasks_file: Path to tasks JSON file
            
        Returns:
            List of validated Task objects
            
        Raises:
            TaskValidationError: If validation fails
        """
        valid_tasks, errors = cls.validate_tasks_file(tasks_file)
        
        if errors:
            error_msg = "Task validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise TaskValidationError(error_msg)
        
        return valid_tasks

