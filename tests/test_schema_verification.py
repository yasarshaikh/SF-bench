"""
Tests for schema result verification.
"""
from sfbench.utils.schema import EvaluationReport, EvaluationSummary, InstanceResult, TaskStatus, ValidationBreakdown, ComponentStatus
from sfbench.utils.checkpoint import generate_evaluation_hash
from pathlib import Path
import tempfile


def test_evaluation_hash_in_schema():
    """Test that evaluation hash can be added to schema."""
    report = EvaluationReport(
        model_name="test-model",
        dataset="test"
    )
    
    # Add hash
    report.evaluation_hash = "test-hash-123"
    report.model_config = {"provider": "test", "model": "test-model"}
    
    # Convert to dict
    report_dict = report.to_dict()
    
    assert "evaluation_hash" in report_dict
    assert report_dict["evaluation_hash"] == "test-hash-123"
    assert "model_config" in report_dict
    assert report_dict["model_config"]["provider"] == "test"
    
    print("✅ Evaluation hash in schema test passed")


def test_schema_serialization():
    """Test that schema can be serialized to JSON."""
    report = EvaluationReport(
        model_name="test-model",
        dataset="test"
    )
    
    # Add instance
    instance = InstanceResult(
        instance_id="test-instance",
        model_name="test-model",
        status=TaskStatus.RESOLVED,
        resolved=True
    )
    instance.validation.deployment_status = ComponentStatus.PASS
    instance.validation.deployment_points = 10
    
    report.add_instance(instance)
    report.calculate_summary()
    
    # Serialize to JSON
    import json
    report_dict = report.to_dict()
    json_str = json.dumps(report_dict, indent=2)
    
    # Deserialize
    loaded_dict = json.loads(json_str)
    assert loaded_dict["model_name"] == "test-model"
    assert len(loaded_dict["instances"]) == 1
    assert loaded_dict["instances"][0]["resolved"] is True
    
    print("✅ Schema serialization test passed")


if __name__ == "__main__":
    test_evaluation_hash_in_schema()
    test_schema_serialization()
    print("\n✅ All schema verification tests passed!")
