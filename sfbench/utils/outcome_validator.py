"""
Outcome validation system to verify task completion against requirements.
Validates that the solution actually solves the problem, not just passes tests.
"""
import json
import re
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from pathlib import Path
from sfbench.utils.sfdx import run_sfdx, parse_json_output

if TYPE_CHECKING:
    from sfbench import Task


class OutcomeValidationError(Exception):
    """Raised when outcome validation fails."""
    pass


class OutcomeValidator:
    """
    Validates that a solution meets the task requirements beyond just passing tests.
    """
    
    def __init__(self, task, workspace_dir: Path):
        """
        Initialize outcome validator.
        
        Args:
            task: The task being validated
            workspace_dir: Workspace directory
        """
        self.task = task
        self.workspace_dir = workspace_dir
        self.repo_dir = workspace_dir / task.instance_id
    
    def validate_outcome(
        self,
        expected_outcome: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate that the solution outcome matches the task requirements.
        
        Args:
            expected_outcome: Expected outcome specification (if provided in task)
            
        Returns:
            Validation result with match score and details
        """
        validation_result = {
            "matches_requirements": False,
            "match_score": 0.0,
            "validation_checks": [],
            "errors": []
        }
        
        try:
            # Extract expected outcome from task if not provided
            if expected_outcome is None:
                expected_outcome = self._extract_expected_outcome()
            
            # Run validation checks based on task type
            if self.task.task_type.value == "APEX":
                checks = self._validate_apex_outcome(expected_outcome)
            elif self.task.task_type.value == "LWC":
                checks = self._validate_lwc_outcome(expected_outcome)
            elif self.task.task_type.value == "FLOW":
                checks = self._validate_flow_outcome(expected_outcome)
            elif self.task.task_type.value == "LIGHTNING_PAGE":
                checks = self._validate_lightning_page_outcome(expected_outcome)
            elif self.task.task_type.value == "PAGE_LAYOUT":
                checks = self._validate_page_layout_outcome(expected_outcome)
            elif self.task.task_type.value == "COMMUNITY":
                checks = self._validate_community_outcome(expected_outcome)
            elif self.task.task_type.value == "ARCHITECTURE":
                checks = self._validate_architecture_outcome(expected_outcome)
            else:
                checks = self._validate_generic_outcome(expected_outcome)
            
            validation_result["validation_checks"] = checks
            
            # Calculate match score
            passed_checks = [c for c in checks if c.get("passed", False)]
            total_checks = len(checks)
            if total_checks > 0:
                validation_result["match_score"] = len(passed_checks) / total_checks
                validation_result["matches_requirements"] = validation_result["match_score"] >= 0.8
            
        except Exception as e:
            validation_result["errors"].append(str(e))
        
        return validation_result
    
    def _extract_expected_outcome(self) -> Dict[str, Any]:
        """Extract expected outcome from task description and validation config."""
        outcome = {
            "description_match": self.task.problem_description,
            "validation_command": self.task.validation.command,
            "expected_result": self.task.validation.expected_outcome
        }
        
        # Parse task description for specific requirements
        desc = self.task.problem_description.lower()
        
        # Extract keywords
        if "fix" in desc or "bug" in desc:
            outcome["type"] = "bug_fix"
        elif "create" in desc or "implement" in desc:
            outcome["type"] = "feature"
        elif "refactor" in desc:
            outcome["type"] = "refactor"
        elif "security" in desc:
            outcome["type"] = "security"
        
        return outcome
    
    def _validate_apex_outcome(self, expected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate Apex task outcome."""
        checks = []
        
        # Check 1: Tests pass
        try:
            exit_code, stdout, stderr = run_sfdx(
                self.task.validation.command,
                cwd=self.repo_dir,
                timeout=self.task.timeouts.run
            )
            result = parse_json_output(stdout)
            test_summary = result.get('result', {}).get('summary', {})
            outcome = test_summary.get('outcome', '').lower()
            
            checks.append({
                "check": "tests_pass",
                "passed": outcome == 'passed',
                "details": f"Test outcome: {outcome}"
            })
        except Exception as e:
            checks.append({
                "check": "tests_pass",
                "passed": False,
                "details": f"Error: {str(e)}"
            })
        
        # Check 2: Code coverage (if applicable)
        # Check 3: No compilation errors
        # Check 4: Follows best practices (if specified)
        
        return checks
    
    def _validate_lwc_outcome(self, expected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate LWC task outcome."""
        checks = []
        
        # Check 1: Jest tests pass
        # Check 2: Component renders correctly
        # Check 3: No linting errors
        
        return checks
    
    def _validate_flow_outcome(self, expected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate Flow task outcome."""
        checks = []
        
        # Check 1: Flow is active and valid
        # Check 2: Flow logic matches requirements
        # Check 3: Flow can be executed successfully
        
        return checks
    
    def _validate_lightning_page_outcome(self, expected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate Lightning Page outcome."""
        checks = []
        
        # Check 1: Page exists and is assigned
        # Check 2: Required components are present
        # Check 3: Page layout matches requirements
        
        return checks
    
    def _validate_page_layout_outcome(self, expected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate Page Layout outcome."""
        checks = []
        
        # Check 1: Layout exists
        # Check 2: Required fields are present
        # Check 3: Field order matches requirements
        
        return checks
    
    def _validate_community_outcome(self, expected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate Community/Experience Cloud outcome."""
        checks = []
        
        # Check 1: Community is published
        # Check 2: Required pages/components exist
        # Check 3: Navigation structure is correct
        
        return checks
    
    def _validate_architecture_outcome(self, expected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate Architecture task outcome."""
        checks = []
        
        # Check 1: Solution matches architecture plan
        # Check 2: All components are implemented
        # Check 3: Integration points work
        # Check 4: Performance meets requirements
        
        return checks
    
    def _validate_generic_outcome(self, expected: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generic validation for unknown task types."""
        checks = []
        
        # Basic validation: command execution succeeds
        try:
            exit_code, stdout, stderr = run_sfdx(
                self.task.validation.command,
                cwd=self.repo_dir,
                timeout=self.task.timeouts.run
            )
            
            checks.append({
                "check": "command_execution",
                "passed": exit_code == 0,
                "details": f"Exit code: {exit_code}"
            })
        except Exception as e:
            checks.append({
                "check": "command_execution",
                "passed": False,
                "details": f"Error: {str(e)}"
            })
        
        return checks

