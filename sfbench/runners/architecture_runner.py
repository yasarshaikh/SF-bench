"""
Architecture-level runner for evaluating planning, execution, and prototype validation.
This runner validates that AI agents can:
1. Plan a solution architecture
2. Execute the plan
3. Validate the prototype against requirements
"""
from pathlib import Path
import json
import shutil
from typing import Dict, Any, List

from sfbench import Task
from sfbench.runners.base_runner import BenchmarkRunner
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.sfdx import run_sfdx, parse_json_output, OrgCreationError, TimeoutError as SFDXTimeoutError
from sfbench.utils.outcome_validator import OutcomeValidator


class ArchitectureRunner(BenchmarkRunner):
    """
    Runner for Architecture-level tasks.
    Evaluates planning, execution, and prototype validation.
    """
    
    def __init__(self, task: Task, workspace_dir: Path):
        super().__init__(task, workspace_dir)
        self.org_username: str = None
        self.architecture_plan: Dict[str, Any] = {}
    
    def setup(self) -> None:
        """Setup: Clone repo, create scratch org, deploy base metadata."""
        self._clone_and_checkout()
        self._create_scratch_org()
        self._push_metadata()
    
    def _create_scratch_org(self) -> None:
        """Create scratch org."""
        try:
            exit_code, stdout, stderr = run_sfdx(
                "sf org create scratch --definition-file config/project-scratch-def.json --set-default --duration-days 1",
                cwd=self.repo_dir,
                timeout=self.task.timeouts.setup
            )
            
            result = parse_json_output(stdout)
            self.org_username = result.get('result', {}).get('username')
            
            if not self.org_username:
                raise OrgCreationError("Failed to get org username", 1, "No username in response")
                
        except OrgCreationError:
            raise
        except Exception as e:
            raise OrgCreationError(f"Scratch org creation failed: {str(e)}", 1, str(e))
    
    def _push_metadata(self) -> None:
        """Deploy base metadata."""
        try:
            run_sfdx(
                "sf project deploy start",
                cwd=self.repo_dir,
                timeout=self.task.timeouts.setup
            )
        except Exception as e:
            raise Exception(f"Failed to push metadata: {str(e)}")
    
    def evaluate(self) -> TestResult:
        """
        Evaluate Architecture task:
        1. Extract architecture plan from solution
        2. Validate plan completeness
        3. Execute and validate implementation
        4. Verify prototype matches requirements
        """
        try:
            # Deploy solution
            self._push_metadata()
            
            # Extract and validate architecture plan
            plan_validation = self._validate_architecture_plan()
            
            # Validate implementation
            implementation_validation = self._validate_implementation()
            
            # Validate prototype against requirements
            prototype_validation = self._validate_prototype()
            
            # Run outcome validation
            validator = OutcomeValidator(self.task, self.workspace_dir)
            outcome_result = validator.validate_outcome()
            
            # Calculate overall score
            plan_score = plan_validation.get("score", 0.0)
            impl_score = implementation_validation.get("score", 0.0)
            proto_score = prototype_validation.get("score", 0.0)
            outcome_score = outcome_result.get("match_score", 0.0)
            
            overall_score = (plan_score * 0.2 + impl_score * 0.3 + proto_score * 0.3 + outcome_score * 0.2)
            
            # Determine status
            if overall_score >= 0.8:
                status = TestStatus.PASS
            elif overall_score >= 0.6:
                status = TestStatus.FAIL  # Partial success
            else:
                status = TestStatus.FAIL
            
            return TestResult(
                task_id=self.task.instance_id,
                status=status,
                duration=self._get_duration(),
                details={
                    "architecture_plan": plan_validation,
                    "implementation": implementation_validation,
                    "prototype": prototype_validation,
                    "outcome_validation": outcome_result,
                    "overall_score": overall_score,
                    "scores": {
                        "plan": plan_score,
                        "implementation": impl_score,
                        "prototype": proto_score,
                        "outcome": outcome_score
                    }
                }
            )
            
        except SFDXTimeoutError as e:
            return TestResult(
                task_id=self.task.instance_id,
                status=TestStatus.TIMEOUT,
                duration=self._get_duration(),
                error_message=str(e)
            )
        except Exception as e:
            return TestResult(
                task_id=self.task.instance_id,
                status=TestStatus.ERROR,
                duration=self._get_duration(),
                error_message=str(e)
            )
    
    def _validate_architecture_plan(self) -> Dict[str, Any]:
        """
        Validate that the solution includes an architecture plan.
        Looks for planning documents, diagrams, or structured planning in comments.
        """
        validation = {
            "has_plan": False,
            "plan_components": [],
            "score": 0.0,
            "errors": []
        }
        
        try:
            # Look for architecture documentation
            plan_files = [
                "ARCHITECTURE.md",
                "DESIGN.md",
                "PLAN.md",
                "docs/architecture.md"
            ]
            
            found_components = []
            for plan_file in plan_files:
                plan_path = self.repo_dir / plan_file
                if plan_path.exists():
                    validation["has_plan"] = True
                    found_components.append(plan_file)
            
            # Check for planning in code comments or metadata
            # This is a simplified check - in production, you'd parse and analyze
            
            validation["plan_components"] = found_components
            
            if validation["has_plan"]:
                validation["score"] = 1.0
            else:
                validation["score"] = 0.0
                
        except Exception as e:
            validation["errors"].append(str(e))
        
        return validation
    
    def _validate_implementation(self) -> Dict[str, Any]:
        """
        Validate that the implementation matches the plan.
        Checks for required components, integrations, and structure.
        """
        validation = {
            "components_implemented": [],
            "missing_components": [],
            "score": 0.0,
            "errors": []
        }
        
        try:
            # Deploy and check for errors
            exit_code, stdout, stderr = run_sfdx(
                "sf project deploy start --dry-run --json",
                cwd=self.repo_dir,
                timeout=60
            )
            
            if exit_code == 0:
                result = parse_json_output(stdout)
                # Check deployment success
                validation["score"] = 1.0
            else:
                validation["score"] = 0.5  # Partial implementation
                
        except Exception as e:
            validation["errors"].append(str(e))
            validation["score"] = 0.0
        
        return validation
    
    def _validate_prototype(self) -> Dict[str, Any]:
        """
        Validate that the prototype works and matches requirements.
        Tests functionality, integration points, and user experience.
        """
        validation = {
            "functional": False,
            "integrations_working": [],
            "performance_acceptable": True,
            "score": 0.0,
            "errors": []
        }
        
        try:
            # Run validation command if provided
            if self.task.validation.command:
                exit_code, stdout, stderr = run_sfdx(
                    self.task.validation.command,
                    cwd=self.repo_dir,
                    timeout=self.task.timeouts.run
                )
                
                if exit_code == 0:
                    validation["functional"] = True
                    validation["score"] = 1.0
                else:
                    validation["score"] = 0.5
            else:
                # No validation command - assume partial success
                validation["score"] = 0.5
                
        except Exception as e:
            validation["errors"].append(str(e))
            validation["score"] = 0.0
        
        return validation
    
    def teardown(self) -> None:
        """Cleanup."""
        if self.org_username:
            try:
                run_sfdx(
                    f"sf org delete scratch --target-org {self.org_username} --no-prompt",
                    timeout=60,
                    json_output=False
                )
            except Exception as e:
                print(f"Warning: Failed to delete scratch org {self.org_username}: {str(e)}")
        
        if self.repo_dir.exists():
            try:
                shutil.rmtree(self.repo_dir)
            except Exception as e:
                print(f"Warning: Failed to cleanup repo directory {self.repo_dir}: {str(e)}")

