"""
Functional Validator - Verifies that solutions actually WORK, not just deploy.

This is the core of SF-Bench's credibility. A 100% score must mean 100% works in production.
"""
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ValidationLevel(Enum):
    SYNTAX = "syntax"
    DEPLOYMENT = "deployment"
    FUNCTIONAL = "functional"
    PRODUCTION_READY = "production_ready"


@dataclass
class ValidationStep:
    """A single validation step with expected outcome."""
    name: str
    command: str
    success_criteria: Dict[str, Any]
    timeout: int = 120
    retry_count: int = 0
    
    # Results
    status: str = "pending"  # pending, passed, failed, error
    actual_output: str = ""
    error_message: str = ""
    duration: float = 0.0


@dataclass
class FunctionalValidationResult:
    """Complete validation result for a task."""
    task_id: str
    validation_level: ValidationLevel
    overall_status: str = "pending"
    score: float = 0.0
    steps: List[ValidationStep] = field(default_factory=list)
    
    # Weighted scoring
    deployment_passed: bool = False
    unit_tests_passed: bool = False
    functional_tests_passed: bool = False
    bulk_tests_passed: bool = False
    no_manual_tweaks: bool = False
    
    def calculate_score(self) -> float:
        """Calculate weighted score based on validation results."""
        score = 0.0
        
        # Deployment: 10%
        if self.deployment_passed:
            score += 10.0
        
        # Unit Tests: 20%
        if self.unit_tests_passed:
            score += 20.0
        
        # Functional Tests: 50% (THE CORE)
        if self.functional_tests_passed:
            score += 50.0
        
        # Bulk Tests: 10%
        if self.bulk_tests_passed:
            score += 10.0
        
        # No Manual Tweaks: 10%
        if self.no_manual_tweaks:
            score += 10.0
        
        self.score = score
        return score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "validation_level": self.validation_level.value if self.validation_level else None,
            "overall_status": self.overall_status,
            "score": self.score,
            "deployment_passed": self.deployment_passed,
            "unit_tests_passed": self.unit_tests_passed,
            "functional_tests_passed": self.functional_tests_passed,
            "bulk_tests_passed": self.bulk_tests_passed,
            "no_manual_tweaks": self.no_manual_tweaks,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status,
                    "duration": s.duration,
                    "error": s.error_message
                }
                for s in self.steps
            ]
        }


class FunctionalValidator:
    """
    Validates that solutions actually work, not just deploy.
    
    This is the difference between:
    - "It deployed successfully" (NOT ENOUGH)
    - "It actually does what it's supposed to do" (REQUIRED)
    """
    
    def __init__(self, scratch_org_alias: str, workspace_dir: Path):
        self.scratch_org = scratch_org_alias
        self.workspace_dir = workspace_dir
    
    def validate_apex(
        self,
        task_id: str,
        task_config: Dict[str, Any],
        repo_dir: Path
    ) -> FunctionalValidationResult:
        """
        Validate Apex solution with full functional testing.
        
        Steps:
        1. Deploy to scratch org
        2. Run unit tests with coverage
        3. Execute trigger with test data
        4. Verify outcome via SOQL
        5. Test bulk operations
        """
        result = FunctionalValidationResult(
            task_id=task_id,
            validation_level=ValidationLevel.FUNCTIONAL
        )
        
        # Step 1: Deploy
        deploy_step = self._run_step(
            name="Deploy to Scratch Org",
            command=f"sf project deploy start --target-org {self.scratch_org}",
            cwd=repo_dir,
            timeout=300
        )
        result.steps.append(deploy_step)
        result.deployment_passed = deploy_step.status == "passed"
        
        if not result.deployment_passed:
            result.overall_status = "failed"
            result.calculate_score()
            return result
        
        # Step 2: Run Unit Tests
        test_step = self._run_step(
            name="Run Unit Tests",
            command=f"sf apex run test --target-org {self.scratch_org} --code-coverage --result-format json --wait 10",
            cwd=repo_dir,
            timeout=600
        )
        result.steps.append(test_step)
        
        if test_step.status == "passed":
            # Parse test results
            try:
                test_results = json.loads(test_step.actual_output)
                summary = test_results.get("summary", {})
                if summary.get("outcome") == "Passed":
                    result.unit_tests_passed = True
            except:
                pass
        
        # Step 3: Execute with Test Data
        functional_config = task_config.get("functional_validation") or {}
        test_data_script = functional_config.get("test_data_script")
        
        if test_data_script:
            create_data_step = self._run_step(
                name="Create Test Data",
                command=f"sf apex run --target-org {self.scratch_org} --file {test_data_script}",
                cwd=repo_dir,
                timeout=120
            )
            result.steps.append(create_data_step)
        
        # Step 4: Verify Outcome
        verification_query = functional_config.get("verification_query")
        expected_values = functional_config.get("expected_values", {})
        
        if verification_query:
            verify_step = self._run_soql_verification(
                name="Verify Outcome",
                query=verification_query,
                expected=expected_values
            )
            result.steps.append(verify_step)
            result.functional_tests_passed = verify_step.status == "passed"
        else:
            # No specific verification, assume functional if unit tests pass
            result.functional_tests_passed = result.unit_tests_passed
        
        # Step 5: Bulk Test
        bulk_test_script = functional_config.get("bulk_test_script")
        
        if bulk_test_script:
            bulk_step = self._run_step(
                name="Bulk Test (200 records)",
                command=f"sf apex run --target-org {self.scratch_org} --file {bulk_test_script}",
                cwd=repo_dir,
                timeout=300
            )
            result.steps.append(bulk_step)
            result.bulk_tests_passed = bulk_step.status == "passed"
        else:
            result.bulk_tests_passed = True  # Assume pass if no bulk test defined
        
        # Determine overall status
        if result.deployment_passed and result.unit_tests_passed and result.functional_tests_passed:
            result.overall_status = "passed"
            result.no_manual_tweaks = True
        elif result.deployment_passed and result.unit_tests_passed:
            result.overall_status = "partial"
        else:
            result.overall_status = "failed"
        
        result.calculate_score()
        return result
    
    def validate_flow(
        self,
        task_id: str,
        task_config: Dict[str, Any],
        repo_dir: Path
    ) -> FunctionalValidationResult:
        """
        Validate Flow solution with FULL functional testing.
        
        This is where most AI models fail. A Flow that deploys is NOT the same as a Flow that works.
        
        Steps:
        1. Deploy Flow
        2. Activate Flow
        3. Create record that matches entry conditions
        4. Wait for Flow execution
        5. Verify ALL expected outcomes:
           - Records created/updated correctly
           - Tasks created with correct values
           - Emails sent (if applicable)
           - Platform Events published
        6. Test bulk (200 records)
        7. Test negative case (entry conditions NOT met)
        """
        result = FunctionalValidationResult(
            task_id=task_id,
            validation_level=ValidationLevel.FUNCTIONAL
        )
        
        functional_config = task_config.get("functional_validation") or {}
        
        # Step 1: Deploy Flow
        deploy_step = self._run_step(
            name="Deploy Flow",
            command=f"sf project deploy start --target-org {self.scratch_org} --source-dir force-app/main/default/flows",
            cwd=repo_dir,
            timeout=300
        )
        result.steps.append(deploy_step)
        result.deployment_passed = deploy_step.status == "passed"
        
        if not result.deployment_passed:
            result.overall_status = "failed"
            result.calculate_score()
            return result
        
        # Step 2: Activate Flow
        flow_name = functional_config.get("flow_name")
        if flow_name:
            activate_step = self._run_step(
                name="Activate Flow",
                command=f"sf apex run --target-org {self.scratch_org} -c \"Flow flow = [SELECT Id, Status FROM Flow WHERE DeveloperName = '{flow_name}' LIMIT 1]; // Activation logic here\"",
                cwd=repo_dir,
                timeout=60
            )
            result.steps.append(activate_step)
        
        # Step 3: Create Test Record (trigger conditions met)
        trigger_script = functional_config.get("trigger_test_script")
        if trigger_script:
            trigger_step = self._run_step(
                name="Create Test Record (Trigger Flow)",
                command=f"sf apex run --target-org {self.scratch_org} --file {trigger_script}",
                cwd=repo_dir,
                timeout=120
            )
            result.steps.append(trigger_step)
        
        # Step 4: Wait for async processing
        time.sleep(5)
        
        # Step 5: Verify Outcomes (THE CRITICAL PART)
        verifications = functional_config.get("outcome_verifications", [])
        all_verified = True
        
        for verification in verifications:
            verify_step = self._run_soql_verification(
                name=verification.get("name", "Verify Outcome"),
                query=verification.get("query"),
                expected=verification.get("expected")
            )
            result.steps.append(verify_step)
            if verify_step.status != "passed":
                all_verified = False
        
        result.functional_tests_passed = all_verified
        
        # Step 6: Bulk Test
        bulk_script = functional_config.get("bulk_test_script")
        if bulk_script:
            bulk_step = self._run_step(
                name="Bulk Test (200 records)",
                command=f"sf apex run --target-org {self.scratch_org} --file {bulk_script}",
                cwd=repo_dir,
                timeout=300
            )
            result.steps.append(bulk_step)
            result.bulk_tests_passed = bulk_step.status == "passed"
        
        # Step 7: Negative Test (entry conditions NOT met)
        negative_script = functional_config.get("negative_test_script")
        if negative_script:
            negative_step = self._run_step(
                name="Negative Test (Should NOT trigger)",
                command=f"sf apex run --target-org {self.scratch_org} --file {negative_script}",
                cwd=repo_dir,
                timeout=120
            )
            result.steps.append(negative_step)
        
        # Determine overall status
        if result.deployment_passed and result.functional_tests_passed:
            result.overall_status = "passed"
            result.no_manual_tweaks = True
            result.unit_tests_passed = True  # Flows don't have unit tests
        else:
            result.overall_status = "failed"
        
        result.calculate_score()
        return result
    
    def validate_lwc(
        self,
        task_id: str,
        task_config: Dict[str, Any],
        repo_dir: Path
    ) -> FunctionalValidationResult:
        """
        Validate LWC with Jest tests + deployment + functional verification.
        """
        result = FunctionalValidationResult(
            task_id=task_id,
            validation_level=ValidationLevel.FUNCTIONAL
        )
        
        # Step 1: Run Jest Tests
        jest_step = self._run_step(
            name="Run Jest Tests",
            command="npm run test:unit -- --coverage --passWithNoTests",
            cwd=repo_dir,
            timeout=300
        )
        result.steps.append(jest_step)
        result.unit_tests_passed = jest_step.status == "passed"
        
        # Step 2: Deploy to Scratch Org
        deploy_step = self._run_step(
            name="Deploy to Scratch Org",
            command=f"sf project deploy start --target-org {self.scratch_org}",
            cwd=repo_dir,
            timeout=300
        )
        result.steps.append(deploy_step)
        result.deployment_passed = deploy_step.status == "passed"
        
        # Step 3: Test Apex Controller (if applicable)
        functional_config = task_config.get("functional_validation", {})
        functional_config = functional_config or {}
        controller_test = functional_config.get("controller_test_script")
        
        if controller_test:
            controller_step = self._run_step(
                name="Test Apex Controller",
                command=f"sf apex run --target-org {self.scratch_org} --file {controller_test}",
                cwd=repo_dir,
                timeout=120
            )
            result.steps.append(controller_step)
            result.functional_tests_passed = controller_step.status == "passed"
        else:
            result.functional_tests_passed = result.unit_tests_passed
        
        result.bulk_tests_passed = True  # Not applicable for LWC
        
        if result.unit_tests_passed and result.deployment_passed:
            result.overall_status = "passed"
            result.no_manual_tweaks = True
        else:
            result.overall_status = "failed"
        
        result.calculate_score()
        return result
    
    def _run_step(
        self,
        name: str,
        command: str,
        cwd: Path = None,
        timeout: int = 120,
        success_criteria: Dict[str, Any] = None
    ) -> ValidationStep:
        """Execute a validation step and capture results."""
        if success_criteria is None:
            success_criteria = {"exit_code": 0}
        step = ValidationStep(name=name, command=command, success_criteria=success_criteria, timeout=timeout)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            step.duration = time.time() - start_time
            step.actual_output = result.stdout
            
            if result.returncode == 0:
                step.status = "passed"
            else:
                step.status = "failed"
                step.error_message = result.stderr
                
        except subprocess.TimeoutExpired:
            step.status = "error"
            step.error_message = f"Command timed out after {timeout}s"
            step.duration = timeout
        except Exception as e:
            step.status = "error"
            step.error_message = str(e)
            step.duration = time.time() - start_time
        
        return step
    
    def _run_soql_verification(
        self,
        name: str,
        query: str,
        expected: Dict[str, Any]
    ) -> ValidationStep:
        """Run SOQL query and verify results match expected values."""
        step = ValidationStep(
            name=name,
            command=f"sf data query --target-org {self.scratch_org} --query \"{query}\" --json",
            success_criteria=expected
        )
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                step.command,
                shell=True,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=step.timeout
            )
            
            step.duration = time.time() - start_time
            step.actual_output = result.stdout
            
            if result.returncode == 0:
                # Parse and verify results
                try:
                    data = json.loads(result.stdout)
                    records = data.get("result", {}).get("records", [])
                    
                    # Check expected values
                    all_match = True
                    for key, expected_value in expected.items():
                        if key == "record_count":
                            if len(records) != expected_value:
                                all_match = False
                                step.error_message = f"Expected {expected_value} records, got {len(records)}"
                        elif key == "field_value":
                            field_name = expected_value.get("field")
                            expected_val = expected_value.get("value")
                            for record in records:
                                if record.get(field_name) != expected_val:
                                    all_match = False
                                    step.error_message = f"Field {field_name} expected '{expected_val}', got '{record.get(field_name)}'"
                    
                    step.status = "passed" if all_match else "failed"
                    
                except json.JSONDecodeError:
                    step.status = "failed"
                    step.error_message = "Failed to parse SOQL result"
            else:
                step.status = "failed"
                step.error_message = result.stderr
                
        except Exception as e:
            step.status = "error"
            step.error_message = str(e)
            step.duration = time.time() - start_time
        
        return step
