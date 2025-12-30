from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum


class TaskType(Enum):
    # Development Tasks
    APEX = "APEX"
    LWC = "LWC"
    FLOW = "FLOW"
    DEPLOY = "DEPLOY"
    
    # Configuration Tasks
    LIGHTNING_PAGE = "LIGHTNING_PAGE"
    PAGE_LAYOUT = "PAGE_LAYOUT"
    COMMUNITY = "COMMUNITY"
    PROFILE = "PROFILE"
    PERMISSION_SET = "PERMISSION_SET"
    
    # Cloud-Specific Tasks
    SALES_CLOUD = "SALES_CLOUD"
    SERVICE_CLOUD = "SERVICE_CLOUD"
    MARKETING_CLOUD = "MARKETING_CLOUD"
    COMMERCE_CLOUD = "COMMERCE_CLOUD"
    PLATFORM_CLOUD = "PLATFORM_CLOUD"
    
    # Architecture Tasks
    ARCHITECTURE = "ARCHITECTURE"
    INTEGRATION = "INTEGRATION"
    DATA_MODEL = "DATA_MODEL"
    SECURITY = "SECURITY"


@dataclass
class ValidationConfig:
    """Validation configuration for a task."""
    command: str
    expected_outcome: str
    code_checks: Optional[List[str]] = None
    additional_checks: Optional[Dict[str, Any]] = None


@dataclass
class TimeoutConfig:
    """Timeout configuration for a task."""
    setup: int
    run: int
    functional_test: Optional[int] = None


@dataclass
class Task:
    """
    A benchmark task definition.
    
    Following SWE-bench methodology, each task should have a golden_patch
    (verified human solution) to ensure the task is solvable before asking AI to solve it.
    """
    instance_id: str
    task_type: TaskType
    repo_url: str
    base_commit: str
    problem_description: str
    validation: ValidationConfig
    timeouts: TimeoutConfig
    metadata: Optional[Dict[str, Any]] = None
    functional_validation: Optional[Dict[str, Any]] = None
    test_scripts: Optional[Dict[str, str]] = None
    golden_patch: Optional[str] = None  # Reference to verified solution (diff format)
    golden_patch_path: Optional[str] = None  # Path to golden patch file (relative to data/)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task from dictionary."""
        # Parse validation config - handle extra fields gracefully
        validation_data = data.get('validation', {})
        validation = ValidationConfig(
            command=validation_data.get('command', ''),
            expected_outcome=validation_data.get('expected_outcome', ''),
            code_checks=validation_data.get('code_checks'),
            additional_checks=validation_data.get('additional_checks')
        )
        
        # Parse timeout config - handle extra fields gracefully
        timeout_data = data.get('timeouts', {})
        timeouts = TimeoutConfig(
            setup=timeout_data.get('setup', 600),
            run=timeout_data.get('run', 300),
            functional_test=timeout_data.get('functional_test')
        )
        
        return cls(
            instance_id=data['instance_id'],
            task_type=TaskType(data['task_type']),
            repo_url=data['repo_url'],
            base_commit=data['base_commit'],
            problem_description=data['problem_description'],
            validation=validation,
            timeouts=timeouts,
            metadata=data.get('metadata'),
            functional_validation=data.get('functional_validation'),
            test_scripts=data.get('test_scripts'),
            golden_patch=data.get('golden_patch'),
            golden_patch_path=data.get('golden_patch_path')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Task to dictionary."""
        result = {
            'instance_id': self.instance_id,
            'task_type': self.task_type.value,
            'repo_url': self.repo_url,
            'base_commit': self.base_commit,
            'problem_description': self.problem_description,
            'validation': {
                'command': self.validation.command,
                'expected_outcome': self.validation.expected_outcome
            },
            'timeouts': {
                'setup': self.timeouts.setup,
                'run': self.timeouts.run
            }
        }
        
        if self.validation.code_checks:
            result['validation']['code_checks'] = self.validation.code_checks
        
        if self.metadata:
            result['metadata'] = self.metadata
        
        if self.functional_validation:
            result['functional_validation'] = self.functional_validation
        
        if self.test_scripts:
            result['test_scripts'] = self.test_scripts
        
        if self.golden_patch:
            result['golden_patch'] = self.golden_patch
        
        if self.golden_patch_path:
            result['golden_patch_path'] = self.golden_patch_path
        
        return result
