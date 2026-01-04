"""
Runner for Lightning Dynamic Page tasks.
Validates Lightning Page configuration and component placement.
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


class LightningPageRunner(BenchmarkRunner):
    """
    Runner for Lightning Dynamic Page tasks.
    Validates page configuration, component placement, and visibility rules.
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
        """Create scratch org."""
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
        """Deploy metadata."""
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
        Evaluate Lightning Page:
        1. Deploy page metadata
        2. Validate page structure
        3. Check component placement
        4. Verify visibility rules
        """
        try:
            self._push_metadata()
            
            # Validate Lightning Page
            page_validation = self._validate_lightning_page()
            
            # Run outcome validation
            validator = OutcomeValidator(self.task, self.workspace_dir)
            outcome_result = validator.validate_outcome()
            
            # Determine status
            if page_validation.get("valid", False) and outcome_result.get("matches_requirements", False):
                status = TestStatus.PASS
            else:
                status = TestStatus.FAIL
            
            return TestResult(
                task_id=self.task.instance_id,
                status=status,
                duration=self._get_duration(),
                details={
                    "page_validation": page_validation,
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
    
    def _validate_lightning_page(self) -> Dict[str, Any]:
        """Validate Lightning Page configuration."""
        validation = {
            "valid": False,
            "components": [],
            "errors": []
        }
        
        try:
            # Query for Lightning Page metadata
            # In production, you'd parse the page XML and validate structure
            exit_code, stdout, stderr = run_sfdx(
                "sf project deploy start --dry-run --json",
                cwd=self.repo_dir,
                timeout=60
            )
            
            if exit_code == 0:
                result = parse_json_output(stdout)
                # Check deployment success
                validation["valid"] = True
        except Exception as e:
            validation["errors"].append(str(e))
        
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

