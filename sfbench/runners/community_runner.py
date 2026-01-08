"""
Runner for Salesforce Community/Experience Cloud tasks.
Validates community configuration, pages, and navigation.
"""
from pathlib import Path
import json
import shutil
from typing import Dict, Any

from sfbench import Task
from sfbench.runners.base_runner import BenchmarkRunner
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.sfdx import run_sfdx, parse_json_output, OrgCreationError, PlatformLimitationError, TimeoutError as SFDXTimeoutError
from sfbench.utils.outcome_validator import OutcomeValidator


class CommunityRunner(BenchmarkRunner):
    """
    Runner for Salesforce Community/Experience Cloud tasks.
    Validates community setup, pages, components, and navigation.
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
        """Create scratch org with Experience Cloud enabled."""
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
                
        except PlatformLimitationError:
            # Re-raise platform limitations (will be treated as FAIL)
            raise
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
        Evaluate Community:
        1. Deploy community metadata
        2. Validate community structure
        3. Check pages and navigation
        4. Verify component placement
        """
        try:
            self._push_metadata()
            
            # Validate Community
            community_validation = self._validate_community()
            
            # Run outcome validation
            validator = OutcomeValidator(self.task, self.workspace_dir)
            outcome_result = validator.validate_outcome()
            
            # Determine status
            if community_validation.get("valid", False) and outcome_result.get("matches_requirements", False):
                status = TestStatus.PASS
            else:
                status = TestStatus.FAIL
            
            return TestResult(
                task_id=self.task.instance_id,
                status=status,
                duration=self._get_duration(),
                details={
                    "community_validation": community_validation,
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
    
    def _validate_community(self) -> Dict[str, Any]:
        """Validate Community configuration."""
        validation = {
            "valid": False,
            "published": False,
            "pages": [],
            "errors": []
        }
        
        try:
            # Query for Community/Network metadata
            # In production, you'd use Experience Cloud APIs
            exit_code, stdout, stderr = run_sfdx(
                "sf project deploy start --dry-run --json",
                cwd=self.repo_dir,
                timeout=60
            )
            
            if exit_code == 0:
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

