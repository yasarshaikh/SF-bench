"""
Tests for audit logging system.
"""
import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from sfbench.utils.audit import AuditLogger, EvaluationAudit


def test_audit_logger_initialization():
    """Test that audit logger initializes correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        logger = AuditLogger("test-eval-001", audit_dir)
        
        assert logger.evaluation_id == "test-eval-001"
        assert logger.audit_dir == audit_dir
        assert audit_dir.exists()


def test_create_audit():
    """Test creating an audit record."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        logger = AuditLogger("test-eval-001", audit_dir)
        
        audit = logger.create_audit(
            model_name="gpt-4",
            task_id="task-001",
            input_data="test input",
            output_data="test output",
            scratch_org_id="org-123"
        )
        
        assert audit.evaluation_id == "test-eval-001"
        assert audit.model_name == "gpt-4"
        assert audit.task_id == "task-001"
        assert audit.scratch_org_id == "org-123"
        assert len(audit.input_hash) == 64  # SHA-256 hex length
        assert len(audit.output_hash) == 64


def test_log_api_call():
    """Test logging an API call."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        logger = AuditLogger("test-eval-001", audit_dir)
        
        audit = logger.create_audit(
            model_name="gpt-4",
            task_id="task-001",
            input_data="test",
            output_data="test"
        )
        
        logger.log_api_call(
            audit=audit,
            provider="openai",
            model="gpt-4",
            request_data={"prompt": "test"},
            response_data={"result": "success"},
            duration_ms=1234.5
        )
        
        assert len(audit.api_calls) == 1
        assert audit.api_calls[0]["provider"] == "openai"
        assert audit.api_calls[0]["duration_ms"] == 1234.5


def test_log_sfdx_command():
    """Test logging a Salesforce CLI command."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        logger = AuditLogger("test-eval-001", audit_dir)
        
        audit = logger.create_audit(
            model_name="gpt-4",
            task_id="task-001",
            input_data="test",
            output_data="test"
        )
        
        logger.log_sfdx_command(
            audit=audit,
            command="sf org create scratch",
            exit_code=0,
            stdout="Success",
            stderr="",
            duration_ms=5000.0
        )
        
        assert len(audit.sfdx_commands) == 1
        assert audit.sfdx_commands[0]["command"] == "sf org create scratch"
        assert audit.sfdx_commands[0]["exit_code"] == 0


def test_audit_persistence():
    """Test that audit records are persisted to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        logger = AuditLogger("test-eval-001", audit_dir)
        
        audit = logger.create_audit(
            model_name="gpt-4",
            task_id="task-001",
            input_data="test",
            output_data="test"
        )
        
        logger.log_api_call(
            audit=audit,
            provider="openai",
            model="gpt-4",
            request_data={"prompt": "test"},
            response_data={"result": "success"},
            duration_ms=1234.5
        )
        
        # Check that file was created
        assert logger.audit_file.exists()
        
        # Load and verify
        with open(logger.audit_file) as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["model_name"] == "gpt-4"
        assert len(data[0]["api_calls"]) == 1


def test_audit_report_generation():
    """Test audit report generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        logger = AuditLogger("test-eval-001", audit_dir)
        
        audit1 = logger.create_audit(
            model_name="gpt-4",
            task_id="task-001",
            input_data="test",
            output_data="test"
        )
        logger.finalize_audit(audit1, "passed")
        
        audit2 = logger.create_audit(
            model_name="gpt-4",
            task_id="task-002",
            input_data="test",
            output_data="test"
        )
        logger.finalize_audit(audit2, "failed")
        
        report = logger.generate_audit_report()
        
        assert report["evaluation_id"] == "test-eval-001"
        assert report["total_tasks"] == 2
        assert report["status_counts"]["passed"] == 1
        assert report["status_counts"]["failed"] == 1


def test_audit_hash_verification():
    """Test that audit hashes are correct."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audit_dir = Path(tmpdir) / "audit"
        logger = AuditLogger("test-eval-001", audit_dir)
        
        input_data = "test input data"
        output_data = "test output data"
        
        audit = logger.create_audit(
            model_name="gpt-4",
            task_id="task-001",
            input_data=input_data,
            output_data=output_data
        )
        
        # Verify hash is SHA-256
        import hashlib
        expected_input_hash = hashlib.sha256(input_data.encode('utf-8')).hexdigest()
        expected_output_hash = hashlib.sha256(output_data.encode('utf-8')).hexdigest()
        
        assert audit.input_hash == expected_input_hash
        assert audit.output_hash == expected_output_hash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
