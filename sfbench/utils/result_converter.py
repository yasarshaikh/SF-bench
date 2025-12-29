"""
Result Converter: TestResult → InstanceResult (Schema v2)

Converts legacy TestResult format to new schema v2 InstanceResult format.
This enables backward compatibility while migrating to standardized reporting.
"""

from typing import Optional, Dict, Any
from sfbench.utils.scoring import TestResult, TestStatus
from sfbench.utils.schema import (
    InstanceResult,
    TaskStatus,
    ValidationBreakdown,
    ComponentStatus
)
from sfbench.validators.functional_validator import FunctionalValidationResult


def convert_test_result_to_instance(
    test_result: TestResult,
    model_name: str,
    functional_result: Optional[FunctionalValidationResult] = None
) -> InstanceResult:
    """
    Convert a TestResult to an InstanceResult (schema v2).
    
    Args:
        test_result: Legacy TestResult object
        model_name: Name of the model being evaluated
        functional_result: Optional functional validation result
    
    Returns:
        InstanceResult in schema v2 format
    """
    # Map TestStatus to TaskStatus
    status_map = {
        TestStatus.PASS: TaskStatus.RESOLVED,
        TestStatus.FAIL: TaskStatus.FAIL,
        TestStatus.ERROR: TaskStatus.ERROR,
        TestStatus.TIMEOUT: TaskStatus.ERROR,
    }
    
    instance = InstanceResult(
        instance_id=test_result.task_id,
        model_name=model_name,
        status=status_map.get(test_result.status, TaskStatus.ERROR),
        resolved=(test_result.status == TestStatus.PASS),
        duration_seconds=test_result.duration,
        error_message=test_result.error_message,
        start_time=test_result.timestamp,
    )
    
    # Create validation breakdown
    validation = ValidationBreakdown()
    
    # If we have functional validation results, use them
    if functional_result:
        # Map functional validation to validation breakdown
        validation.deployment_status = (
            ComponentStatus.PASS if functional_result.deployment_passed
            else ComponentStatus.FAIL
        )
        validation.deployment_points = 10 if functional_result.deployment_passed else 0
        
        validation.unit_test_status = (
            ComponentStatus.PASS if functional_result.unit_tests_passed
            else ComponentStatus.FAIL
        )
        validation.unit_test_points = 20 if functional_result.unit_tests_passed else 0
        
        validation.functional_status = (
            ComponentStatus.PASS if functional_result.functional_tests_passed
            else ComponentStatus.FAIL
        )
        validation.functional_points = 50 if functional_result.functional_tests_passed else 0
        
        validation.bulk_status = (
            ComponentStatus.PASS if functional_result.bulk_operations_passed
            else ComponentStatus.FAIL
        )
        validation.bulk_points = 10 if functional_result.bulk_operations_passed else 0
        
        validation.no_tweaks_status = (
            ComponentStatus.PASS if functional_result.no_manual_tweaks
            else ComponentStatus.FAIL
        )
        validation.no_tweaks_points = 10 if functional_result.no_manual_tweaks else 0
        
        # Use calculated score from functional validator
        if hasattr(functional_result, 'score'):
            validation.total_score = functional_result.score
        else:
            validation.calculate_total()
        
        # Store functional details
        validation.functional_details = {
            "validation_level": functional_result.validation_level.value if functional_result.validation_level else None,
            "steps": [step.to_dict() for step in functional_result.steps] if hasattr(functional_result, 'steps') else []
        }
    else:
        # No functional validation - map from TestResult status
        if test_result.status == TestStatus.PASS:
            validation.deployment_status = ComponentStatus.PASS
            validation.deployment_points = 10
            validation.total_score = 10  # Deployment only
        else:
            validation.deployment_status = ComponentStatus.FAIL
            validation.deployment_points = 0
            validation.total_score = 0
        
        validation.calculate_total()
    
    instance.validation = validation
    
    # Set resolved status based on validation
    if validation.is_resolved():
        instance.mark_resolved()
    elif test_result.status == TestStatus.FAIL:
        instance.mark_failed(test_result.error_message or "Validation failed")
    elif test_result.status == TestStatus.ERROR:
        instance.mark_error("execution_error", test_result.error_message or "Unknown error")
    
    return instance
