"""
SF-Bench Result Schema v2

Standardized result format inspired by SWE-bench for tool compatibility,
academic credibility, and professional presentation.

Schema Design Principles:
- Backward compatible with v1
- JSON-serializable for tool compatibility
- Comprehensive validation breakdown
- Clear status hierarchy
- Academic rigor in reporting
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status."""
    RESOLVED = "resolved"  # Successfully completed
    FAIL = "fail"  # Failed validation
    ERROR = "error"  # Error during execution
    SKIPPED = "skipped"  # Not executed


class ComponentStatus(str, Enum):
    """Individual component validation status."""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class ValidationBreakdown:
    """
    Detailed validation results for each component.
    
    Scoring:
    - Deploy: 10 points
    - Unit Tests: 20 points
    - Functional: 50 points
    - Bulk: 10 points
    - No Tweaks: 10 points
    Total: 100 points
    """
    
    # Deployment validation
    deployment_status: ComponentStatus = ComponentStatus.SKIPPED
    deployment_message: str = ""
    deployment_points: int = 0  # Max: 10
    
    # Unit test validation
    unit_test_status: ComponentStatus = ComponentStatus.SKIPPED
    unit_test_message: str = ""
    unit_test_passed: int = 0
    unit_test_failed: int = 0
    unit_test_total: int = 0
    unit_test_points: int = 0  # Max: 20
    
    # Functional validation
    functional_status: ComponentStatus = ComponentStatus.SKIPPED
    functional_message: str = ""
    functional_details: Dict[str, Any] = field(default_factory=dict)
    functional_points: int = 0  # Max: 50
    
    # Bulk data validation
    bulk_status: ComponentStatus = ComponentStatus.SKIPPED
    bulk_message: str = ""
    bulk_records_processed: int = 0
    bulk_records_expected: int = 200
    bulk_points: int = 0  # Max: 10
    
    # No manual tweaks validation
    no_tweaks_status: ComponentStatus = ComponentStatus.SKIPPED
    no_tweaks_message: str = ""
    no_tweaks_points: int = 0  # Max: 10
    
    # Total score
    total_score: int = 0  # Max: 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def calculate_total(self) -> int:
        """Calculate total score from all components."""
        self.total_score = (
            self.deployment_points +
            self.unit_test_points +
            self.functional_points +
            self.bulk_points +
            self.no_tweaks_points
        )
        return self.total_score
    
    def is_resolved(self) -> bool:
        """
        Check if task is resolved (meets minimum criteria).
        
        CRITICAL: Binary Pass/Fail - Functional requirement MUST be met.
        This follows SWE-bench methodology: if functional requirement isn't met,
        the solution is FAILED, regardless of other checks.
        
        Criteria for RESOLVED (ALL must be true):
        - Deployment: PASS (necessary but not sufficient)
        - Unit Tests: PASS (code quality check)
        - Functional: PASS (THE CORE REQUIREMENT - if this fails, task fails)
        
        Note: Score breakdown (0-100) is kept as diagnostic metadata only.
        The top-level metric is binary: PASS or FAIL.
        """
        # Functional test is the gatekeeper - if it fails, task fails
        if self.functional_status != ComponentStatus.PASS:
            return False
        
        # All other checks must also pass for a complete solution
        return (
            self.deployment_status == ComponentStatus.PASS and
            self.unit_test_status == ComponentStatus.PASS
        )


@dataclass
class InstanceResult:
    """
    Result for a single task instance evaluation.
    
    This is the core unit of evaluation - one model attempting one task.
    """
    
    # Identification
    instance_id: str  # e.g., "lwc-component-001"
    model_name: str  # e.g., "claude-3.5-sonnet"
    
    # Status
    status: TaskStatus = TaskStatus.ERROR
    resolved: bool = False  # True if task successfully completed
    
    # Validation breakdown
    validation: ValidationBreakdown = field(default_factory=ValidationBreakdown)
    
    # Metadata
    duration_seconds: float = 0.0
    scratch_org_username: Optional[str] = None
    scratch_org_creation_time: float = 0.0
    
    # Error tracking
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    
    # Timestamps
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    
    # Logs
    log_path: Optional[str] = None
    
    # Solution
    solution_patch: Optional[str] = None  # The generated solution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert enums to strings
        data['status'] = self.status.value
        return data
    
    def mark_resolved(self):
        """Mark task as successfully resolved."""
        self.status = TaskStatus.RESOLVED
        self.resolved = True
        self.end_time = datetime.utcnow().isoformat()
    
    def mark_failed(self, message: str = ""):
        """Mark task as failed."""
        self.status = TaskStatus.FAIL
        self.resolved = False
        self.error_message = message
        self.end_time = datetime.utcnow().isoformat()
    
    def mark_error(self, error_type: str, message: str):
        """Mark task as errored."""
        self.status = TaskStatus.ERROR
        self.resolved = False
        self.error_type = error_type
        self.error_message = message
        self.end_time = datetime.utcnow().isoformat()


@dataclass
class EvaluationSummary:
    """
    Summary statistics for an evaluation run (SWE-bench compatible).
    """
    
    # Overall metrics (SWE-bench terminology)
    total_instances: int = 0
    instances_submitted: int = 0  # SWE-bench field
    instances_completed: int = 0  # SWE-bench field
    resolved_instances: int = 0
    instances_resolved: int = 0  # SWE-bench field (alias)
    instances_unresolved: int = 0  # SWE-bench field
    failed_instances: int = 0
    error_instances: int = 0
    instances_error: int = 0  # SWE-bench field (alias)
    instances_empty_patch: int = 0  # SWE-bench field
    
    # Success rates
    resolve_rate: float = 0.0  # resolved / total (0.0-1.0)
    resolution_rate: float = 0.0  # SWE-bench field (as percentage 0-100)
    
    # Scoring metrics
    avg_score: float = 0.0
    avg_functional_score: float = 0.0  # SWE-bench field
    median_score: float = 0.0
    min_score: int = 0
    max_score: int = 0
    
    # Component metrics
    deployment_pass_rate: float = 0.0
    unit_test_pass_rate: float = 0.0
    functional_pass_rate: float = 0.0
    bulk_pass_rate: float = 0.0
    no_tweaks_pass_rate: float = 0.0
    
    # Performance metrics
    avg_duration_seconds: float = 0.0
    total_duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class EvaluationReport:
    """
    Complete evaluation report for a model run.
    
    This is the top-level structure that gets saved as JSON.
    """
    
    # Schema version
    schema_version: str = "2.0"
    
    # Run metadata
    run_id: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
    model_name: str = ""
    dataset: str = "verified"  # verified, lite, full
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    instances: List[InstanceResult] = field(default_factory=list)
    summary: EvaluationSummary = field(default_factory=EvaluationSummary)
    
    # Timestamps
    start_time: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    end_time: Optional[str] = None
    
    # Environment info
    environment: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization (SWE-bench compatible format)."""
        # Calculate ID lists (SWE-bench style)
        resolved_ids = sorted([inst.instance_id for inst in self.instances if inst.resolved])
        unresolved_ids = sorted([
            inst.instance_id for inst in self.instances 
            if not inst.resolved and inst.status == TaskStatus.FAIL
        ])
        error_ids = sorted([
            inst.instance_id for inst in self.instances 
            if inst.status == TaskStatus.ERROR
        ])
        empty_patch_ids = sorted([
            inst.instance_id for inst in self.instances 
            if not inst.solution_patch or len(inst.solution_patch.strip()) == 0
        ])
        completed_ids = sorted([
            inst.instance_id for inst in self.instances 
            if inst.status != TaskStatus.ERROR
        ])
        
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "model_name_or_path": self.model_name,  # SWE-bench field name
            "model_name": self.model_name,  # Keep for backward compatibility
            "dataset": self.dataset,
            "created_at": self.start_time,  # SWE-bench field name
            "start_time": self.start_time,  # Keep for backward compatibility
            "end_time": self.end_time,
            "evaluation_config": self.config,  # SWE-bench field name
            "config": self.config,  # Keep for backward compatibility
            "instances": [inst.to_dict() for inst in self.instances],
            "summary": self.summary.to_dict(),
            # SWE-bench style ID lists
            "resolved_ids": resolved_ids,
            "unresolved_ids": unresolved_ids,
            "error_ids": error_ids,
            "empty_patch_ids": empty_patch_ids,
            "completed_ids": completed_ids,
            "environment": self.environment,
        }
    
    def add_instance(self, instance: InstanceResult):
        """Add an instance result to the report."""
        self.instances.append(instance)
    
    def calculate_summary(self):
        """Calculate summary statistics from instances (SWE-bench compatible)."""
        if not self.instances:
            return
        
        # Count statuses (SWE-bench terminology)
        self.summary.total_instances = len(self.instances)
        self.summary.resolved_instances = sum(1 for i in self.instances if i.resolved)
        self.summary.failed_instances = sum(1 for i in self.instances if i.status == TaskStatus.FAIL)
        self.summary.error_instances = sum(1 for i in self.instances if i.status == TaskStatus.ERROR)
        
        # SWE-bench style counts
        instances_submitted = len(self.instances)
        instances_completed = sum(1 for i in self.instances if i.status != TaskStatus.ERROR)
        instances_unresolved = sum(1 for i in self.instances if not i.resolved and i.status == TaskStatus.FAIL)
        instances_empty_patch = sum(1 for i in self.instances if not i.solution_patch or len(i.solution_patch.strip()) == 0)
        
        # Calculate rates (SWE-bench style)
        if self.summary.total_instances > 0:
            self.summary.resolve_rate = self.summary.resolved_instances / self.summary.total_instances
            self.summary.resolution_rate = self.summary.resolve_rate * 100.0  # As percentage
            # Set aliases for SWE-bench compatibility
            self.summary.instances_resolved = self.summary.resolved_instances
            self.summary.instances_error = self.summary.error_instances
            self.summary.instances_submitted = instances_submitted
            self.summary.instances_completed = instances_completed
            self.summary.instances_unresolved = instances_unresolved
            self.summary.instances_empty_patch = instances_empty_patch
        
        # Calculate score statistics
        scores = [i.validation.total_score for i in self.instances]
        functional_scores = [i.validation.functional_points for i in self.instances if i.validation.functional_points > 0]
        if scores:
            self.summary.avg_score = sum(scores) / len(scores)
            self.summary.median_score = sorted(scores)[len(scores) // 2]
            self.summary.min_score = min(scores)
            self.summary.max_score = max(scores)
        if functional_scores:
            self.summary.avg_functional_score = sum(functional_scores) / len(functional_scores)
        
        # Calculate component pass rates
        total = self.summary.total_instances
        if total > 0:
            self.summary.deployment_pass_rate = sum(
                1 for i in self.instances 
                if i.validation.deployment_status == ComponentStatus.PASS
            ) / total
            
            self.summary.unit_test_pass_rate = sum(
                1 for i in self.instances 
                if i.validation.unit_test_status == ComponentStatus.PASS
            ) / total
            
            self.summary.functional_pass_rate = sum(
                1 for i in self.instances 
                if i.validation.functional_status == ComponentStatus.PASS
            ) / total
            
            self.summary.bulk_pass_rate = sum(
                1 for i in self.instances 
                if i.validation.bulk_status == ComponentStatus.PASS
            ) / total
            
            self.summary.no_tweaks_pass_rate = sum(
                1 for i in self.instances 
                if i.validation.no_tweaks_status == ComponentStatus.PASS
            ) / total
        
        # Calculate duration statistics
        durations = [i.duration_seconds for i in self.instances if i.duration_seconds > 0]
        if durations:
            self.summary.avg_duration_seconds = sum(durations) / len(durations)
            self.summary.total_duration_seconds = sum(durations)
        
        # Set end time
        self.end_time = datetime.utcnow().isoformat()
    
    def finalize(self):
        """Finalize the report by calculating all summary statistics."""
        self.calculate_summary()
        self.end_time = datetime.utcnow().isoformat()


# Convenience functions

def create_instance_result(instance_id: str, model_name: str) -> InstanceResult:
    """Create a new instance result with default values."""
    return InstanceResult(
        instance_id=instance_id,
        model_name=model_name,
        validation=ValidationBreakdown()
    )


def create_evaluation_report(model_name: str, dataset: str = "verified", config: Optional[Dict] = None) -> EvaluationReport:
    """Create a new evaluation report."""
    return EvaluationReport(
        model_name=model_name,
        dataset=dataset,
        config=config or {}
    )


# Validation helpers

def validate_schema(data: Dict[str, Any]) -> bool:
    """
    Validate that a dictionary conforms to the schema.
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["schema_version", "run_id", "model_name", "instances", "summary"]
    
    # Check required top-level fields
    for field in required_fields:
        if field not in data:
            return False
    
    # Check schema version
    if data["schema_version"] != "2.0":
        return False
    
    # Check instances structure
    if not isinstance(data["instances"], list):
        return False
    
    for instance in data["instances"]:
        if "instance_id" not in instance or "status" not in instance:
            return False
    
    return True


def migrate_v1_to_v2(v1_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Migrate a v1 result to v2 schema.
    
    v1 format: Simple flat structure
    v2 format: Structured with ValidationBreakdown
    
    Args:
        v1_data: Dictionary in v1 format
    
    Returns:
        Dictionary in v2 format
    """
    # Create v2 report
    report = create_evaluation_report(
        model_name=v1_data.get("model_name", "unknown"),
        dataset=v1_data.get("dataset", "verified")
    )
    
    # Migrate instances
    for v1_instance in v1_data.get("instances", []):
        instance = InstanceResult(
            instance_id=v1_instance.get("instance_id", "unknown"),
            model_name=v1_data.get("model_name", "unknown"),
            status=TaskStatus(v1_instance.get("status", "error")),
            resolved=v1_instance.get("resolved", False),
            duration_seconds=v1_instance.get("duration", 0.0),
            error_message=v1_instance.get("error_message"),
        )
        
        # Migrate validation data
        validation = ValidationBreakdown()
        
        # Map old fields to new structure
        if "score" in v1_instance:
            validation.total_score = v1_instance["score"]
        
        instance.validation = validation
        report.add_instance(instance)
    
    # Calculate summary
    report.calculate_summary()
    
    return report.to_dict()
