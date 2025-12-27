from dataclasses import dataclass
from typing import Dict, Any, Optional
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
    ARCHITECTURE = "ARCHITECTURE"  # Planning, execution, prototype validation
    INTEGRATION = "INTEGRATION"  # API integrations, webhooks
    DATA_MODEL = "DATA_MODEL"  # Schema design, relationships
    SECURITY = "SECURITY"  # Sharing rules, field-level security


@dataclass
class ValidationConfig:
    command: str
    expected_outcome: str


@dataclass
class TimeoutConfig:
    setup: int
    run: int


@dataclass
class Task:
    instance_id: str
    task_type: TaskType
    repo_url: str
    base_commit: str
    problem_description: str
    validation: ValidationConfig
    timeouts: TimeoutConfig
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(
            instance_id=data['instance_id'],
            task_type=TaskType(data['task_type']),
            repo_url=data['repo_url'],
            base_commit=data['base_commit'],
            problem_description=data['problem_description'],
            validation=ValidationConfig(**data['validation']),
            timeouts=TimeoutConfig(**data['timeouts'])
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
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
