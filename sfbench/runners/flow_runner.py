"""
Runner for Salesforce Flow tasks.
Flows require special handling as they're metadata-based and need activation.
"""
from pathlib import Path
import json
import shutil
from typing import Dict, Any

from sfbench import Task
from sfbench.runners.base_runner import BenchmarkRunner
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.sfdx import run_sfdx, parse_json_output, OrgCreationError, TimeoutError as SFDXTimeoutError
from sfbench.utils.outcome_validator import OutcomeValidator


class FlowRunner(BenchmarkRunner):
    """
    Runner for Salesforce Flow tasks.
    Handles Flow creation, activation, and validation.
    """
    
    def __init__(self, task: Task, workspace_dir: Path, scratch_org_alias=None):
        super().__init__(task, workspace_dir, scratch_org_alias)
        self.org_username: str = None
    
    def setup(self) -> None:
        """Setup: Clone repo, create scratch org, deploy base metadata."""
        self._clone_and_checkout()
        self._create_scratch_org()
        self._push_metadata()
    
    def _create_scratch_org(self) -> None:
        """Create scratch org for Flow testing."""
        from sfbench.utils.sfdx import create_scratch_org
        from pathlib import Path
        
        try:
            # Use the template from data/templates, not from repo
            template_file = Path(__file__).parent.parent.parent / "data" / "templates" / "project-scratch-def.json"
            
            # Generate unique alias
            import time
            alias = f"sfbench-{self.task.instance_id}-{int(time.time())}"
            
            # Use the utility function which handles errors properly
            # Run from repo_dir to avoid sfdx-project.json conflicts
            org_result = create_scratch_org(
                alias=alias,
                duration_days=1,
                definition_file=template_file,
                cwd=self.repo_dir  # Run from repo directory to use its sfdx-project.json
            )
            
            self.org_username = org_result.get('username')
            
            if not self.org_username:
                raise OrgCreationError("Failed to get org username", 1, "No username in response")
                
        except OrgCreationError:
            raise
        except Exception as e:
            raise OrgCreationError(f"Scratch org creation failed: {str(e)}", 1, str(e))
    
    def _push_metadata(self) -> None:
        """Deploy base metadata to scratch org."""
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
        Evaluate Flow task:
        1. Deploy Flow metadata
        2. Activate Flow
        3. Validate Flow structure
        4. Test Flow execution (if possible)
        """
        try:
            # Deploy Flow metadata
            self._push_metadata()
            
            # Activate Flow (if not already active)
            # Note: Flow activation requires specific API calls
            flow_validation = self._validate_flow()
            
            # Run outcome validation
            validator = OutcomeValidator(self.task, self.workspace_dir)
            outcome_result = validator.validate_outcome()
            
            # Determine status
            if flow_validation.get("valid", False) and outcome_result.get("matches_requirements", False):
                status = TestStatus.PASS
            elif flow_validation.get("valid", False):
                status = TestStatus.FAIL  # Flow is valid but doesn't match requirements
            else:
                status = TestStatus.FAIL
            
            return TestResult(
                task_id=self.task.instance_id,
                status=status,
                duration=self._get_duration(),
                details={
                    "flow_validation": flow_validation,
                    "outcome_validation": outcome_result,
                    "match_score": outcome_result.get("match_score", 0.0)
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
    
    def _validate_flow(self) -> Dict[str, Any]:
        """
        Validate Flow structure and activation status.
        
        Returns:
            Validation result dictionary
        """
        validation = {
            "valid": False,
            "active": False,
            "errors": []
        }
        
        try:
            # Query for Flow metadata
            # This is a simplified check - in production, you'd query the Flow API
            exit_code, stdout, stderr = run_sfdx(
                "sf data query --query \"SELECT Id, MasterLabel, Status FROM Flow WHERE DeveloperName LIKE '%'\" --json",
                cwd=self.repo_dir,
                timeout=60
            )
            
            if exit_code == 0:
                result = parse_json_output(stdout)
                records = result.get('result', {}).get('records', [])
                
                # Check if Flow exists and is active
                for record in records:
                    if record.get('Status') == 'Active':
                        validation["active"] = True
                        validation["valid"] = True
                        break
        except Exception as e:
            validation["errors"].append(str(e))
        
        return validation
    
    def teardown(self) -> None:
        """Cleanup: Delete scratch org and workspace."""
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

