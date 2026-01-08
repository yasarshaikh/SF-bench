"""
Task Schema Validation

Validates task JSON files against SF-Bench schema.
Inspired by SWE-bench's validation approach.
Enhanced with difficulty validation, bulk operation checks, and quality scoring.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    value: Any = None
    severity: str = "error"  # error, warning, info


@dataclass
class TaskQualityScore:
    """Task quality score breakdown."""
    overall_score: float
    difficulty_score: float
    bulk_operation_score: float
    governor_limit_score: float
    edge_case_score: float
    documentation_score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


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
        "INTEGRATION",
    ]
    
    # Add INTEGRATION to valid types
    if "INTEGRATION" not in VALID_TASK_TYPES:
        VALID_TASK_TYPES.append("INTEGRATION")
    
    VALID_DIFFICULTIES = ["easy", "medium", "hard", "expert"]
    
    BULK_OPERATION_KEYWORDS = [
        "200+", "200 records", "bulk", "bulkification", "governor limit",
        "large dataset", "high volume", "10,000+", "1000+"
    ]
    
    GOVERNOR_LIMIT_KEYWORDS = [
        "governor limit", "soql queries", "dml statements", "cpu time",
        "heap size", "callout limit", "email limit"
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
    
    def validate_difficulty(self, task: Dict[str, Any]) -> List[ValidationError]:
        """
        Validate difficulty level in metadata.
        
        Args:
            task: Task dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if "metadata" in task and isinstance(task["metadata"], dict):
            metadata = task["metadata"]
            if "difficulty" in metadata:
                difficulty = metadata["difficulty"]
                if difficulty not in self.VALID_DIFFICULTIES:
                    errors.append(ValidationError(
                        field="metadata.difficulty",
                        message=f"Invalid difficulty '{difficulty}'. Must be one of: {', '.join(self.VALID_DIFFICULTIES)}",
                        value=difficulty,
                        severity="warning"
                    ))
        
        return errors
    
    def check_bulk_operations(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if task mentions bulk operations (200+ records).
        
        Args:
            task: Task dictionary
            
        Returns:
            Tuple of (has_bulk_mention, list_of_issues)
        """
        issues = []
        has_bulk_mention = False
        
        description = task.get("problem_description", "").lower()
        code_checks = task.get("validation", {}).get("code_checks", [])
        
        # Check description for bulk operation keywords
        for keyword in self.BULK_OPERATION_KEYWORDS:
            if keyword.lower() in description:
                has_bulk_mention = True
                break
        
        # Check code_checks for bulk-related checks
        bulk_checks = ["bulk", "bulkification", "200", "governor"]
        for check in code_checks:
            if any(bulk_keyword in check.lower() for bulk_keyword in bulk_checks):
                has_bulk_mention = True
                break
        
        # If task type is APEX or FLOW, recommend bulk operation testing
        if task.get("task_type") in ["APEX", "FLOW"] and not has_bulk_mention:
            issues.append("Task should mention bulk operation testing (200+ records) for APEX/FLOW tasks")
        
        return has_bulk_mention, issues
    
    def check_governor_limit_awareness(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if task demonstrates governor limit awareness.
        
        Args:
            task: Task dictionary
            
        Returns:
            Tuple of (has_governor_awareness, list_of_issues)
        """
        issues = []
        has_awareness = False
        
        description = task.get("problem_description", "").lower()
        code_checks = task.get("validation", {}).get("code_checks", [])
        
        # Check for governor limit keywords
        for keyword in self.GOVERNOR_LIMIT_KEYWORDS:
            if keyword.lower() in description:
                has_awareness = True
                break
        
        # Check code_checks
        for check in code_checks:
            if "governor" in check.lower() or "limit" in check.lower():
                has_awareness = True
                break
        
        # For APEX tasks, recommend governor limit awareness
        if task.get("task_type") == "APEX" and not has_awareness:
            issues.append("APEX task should demonstrate governor limit awareness")
        
        return has_awareness, issues
    
    def check_edge_case_coverage(self, task: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if task mentions edge case handling.
        
        Args:
            task: Task dictionary
            
        Returns:
            Tuple of (has_edge_cases, list_of_issues)
        """
        issues = []
        has_edge_cases = False
        
        description = task.get("problem_description", "").lower()
        edge_case_keywords = [
            "edge case", "null", "empty", "error handling", "exception",
            "validation", "boundary", "invalid input", "missing data"
        ]
        
        for keyword in edge_case_keywords:
            if keyword in description:
                has_edge_cases = True
                break
        
        if not has_edge_cases:
            issues.append("Task should mention edge case handling (null values, error scenarios)")
        
        return has_edge_cases, issues
    
    def calculate_quality_score(self, task: Dict[str, Any]) -> TaskQualityScore:
        """
        Calculate quality score for a task.
        
        Args:
            task: Task dictionary
            
        Returns:
            TaskQualityScore object
        """
        issues = []
        recommendations = []
        scores = {
            "difficulty": 0.0,
            "bulk_operation": 0.0,
            "governor_limit": 0.0,
            "edge_case": 0.0,
            "documentation": 0.0
        }
        
        # Difficulty validation (20 points)
        if "metadata" in task and isinstance(task["metadata"], dict):
            if "difficulty" in task["metadata"]:
                difficulty = task["metadata"]["difficulty"]
                if difficulty in self.VALID_DIFFICULTIES:
                    scores["difficulty"] = 20.0
                else:
                    issues.append(f"Invalid difficulty: {difficulty}")
            else:
                issues.append("Missing difficulty in metadata")
                recommendations.append("Add difficulty field to metadata (easy/medium/hard/expert)")
        else:
            issues.append("Missing metadata section")
            recommendations.append("Add metadata section with difficulty")
        
        # Bulk operation check (20 points)
        has_bulk, bulk_issues = self.check_bulk_operations(task)
        if has_bulk:
            scores["bulk_operation"] = 20.0
        else:
            issues.extend(bulk_issues)
            if task.get("task_type") in ["APEX", "FLOW"]:
                recommendations.append("Mention bulk operation testing (200+ records)")
        
        # Governor limit awareness (20 points)
        has_governor, governor_issues = self.check_governor_limit_awareness(task)
        if has_governor:
            scores["governor_limit"] = 20.0
        else:
            issues.extend(governor_issues)
            if task.get("task_type") == "APEX":
                recommendations.append("Mention governor limit awareness")
        
        # Edge case coverage (20 points)
        has_edge_cases, edge_issues = self.check_edge_case_coverage(task)
        if has_edge_cases:
            scores["edge_case"] = 20.0
        else:
            issues.extend(edge_issues)
            recommendations.append("Mention edge case handling")
        
        # Documentation (20 points)
        description = task.get("problem_description", "")
        validation = task.get("validation", {})
        code_checks = validation.get("code_checks", [])
        
        doc_score = 0.0
        if len(description) > 200:  # Detailed description
            doc_score += 10.0
        if len(code_checks) >= 3:  # Multiple validation checks
            doc_score += 10.0
        else:
            recommendations.append("Add more code_checks for comprehensive validation")
        
        scores["documentation"] = doc_score
        
        # Calculate overall score
        overall_score = sum(scores.values())
        
        return TaskQualityScore(
            overall_score=overall_score,
            difficulty_score=scores["difficulty"],
            bulk_operation_score=scores["bulk_operation"],
            governor_limit_score=scores["governor_limit"],
            edge_case_score=scores["edge_case"],
            documentation_score=scores["documentation"],
            issues=issues,
            recommendations=recommendations
        )
    
    def validate_task_enhanced(self, task: Dict[str, Any]) -> Tuple[List[ValidationError], TaskQualityScore]:
        """
        Enhanced validation with quality scoring.
        
        Args:
            task: Task dictionary to validate
            
        Returns:
            Tuple of (validation_errors, quality_score)
        """
        errors = self.validate_task(task)
        
        # Add difficulty validation
        errors.extend(self.validate_difficulty(task))
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(task)
        
        return errors, quality_score
    
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
        
        # Group by severity
        error_list = [e for e in errors if e.severity == "error"]
        warning_list = [e for e in errors if e.severity == "warning"]
        info_list = [e for e in errors if e.severity == "info"]
        
        if error_list:
            print(f"❌ Found {len(error_list)} error(s):\n")
            for error in error_list:
                print(f"  • {error.field}: {error.message}")
                if error.value is not None:
                    print(f"    Value: {error.value}")
        
        if warning_list:
            print(f"\n⚠️  Found {len(warning_list)} warning(s):\n")
            for error in warning_list:
                print(f"  • {error.field}: {error.message}")
                if error.value is not None:
                    print(f"    Value: {error.value}")
        
        if info_list:
            print(f"\nℹ️  Found {len(info_list)} info message(s):\n")
            for error in info_list:
                print(f"  • {error.field}: {error.message}")
    
    def print_quality_scores(self, tasks: List[Dict[str, Any]]):
        """Print quality scores for all tasks."""
        print("\n📊 Task Quality Scores:\n")
        print("-" * 80)
        
        for idx, task in enumerate(tasks):
            instance_id = task.get("instance_id", f"task_{idx}")
            quality_score = self.calculate_quality_score(task)
            
            print(f"\n{instance_id}:")
            print(f"  Overall Score: {quality_score.overall_score:.1f}/100")
            print(f"    Difficulty: {quality_score.difficulty_score:.1f}/20")
            print(f"    Bulk Operations: {quality_score.bulk_operation_score:.1f}/20")
            print(f"    Governor Limits: {quality_score.governor_limit_score:.1f}/20")
            print(f"    Edge Cases: {quality_score.edge_case_score:.1f}/20")
            print(f"    Documentation: {quality_score.documentation_score:.1f}/20")
            
            if quality_score.issues:
                print(f"  Issues: {len(quality_score.issues)}")
                for issue in quality_score.issues[:3]:  # Show first 3
                    print(f"    - {issue}")
            
            if quality_score.recommendations:
                print(f"  Recommendations: {len(quality_score.recommendations)}")
                for rec in quality_score.recommendations[:3]:  # Show first 3
                    print(f"    - {rec}")
        
        # Calculate average
        avg_score = sum(self.calculate_quality_score(t).overall_score for t in tasks) / len(tasks) if tasks else 0
        print(f"\n{'=' * 80}")
        print(f"Average Quality Score: {avg_score:.1f}/100")
        print("-" * 80)


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
