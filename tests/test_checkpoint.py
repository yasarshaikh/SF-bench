"""
Tests for checkpoint functionality.
"""
import json
import tempfile
import shutil
from pathlib import Path
from sfbench.utils.checkpoint import CheckpointManager, generate_evaluation_hash


def test_checkpoint_creation():
    """Test checkpoint creation and loading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_dir = Path(tmpdir) / "checkpoints"
        manager = CheckpointManager(checkpoint_dir)
        
        # Create checkpoint
        checkpoint_file = manager.create_checkpoint(
            evaluation_id="test-eval-001",
            completed_tasks=["task-1", "task-2"],
            results={"task-1": {"status": "passed"}, "task-2": {"status": "passed"}},
            metadata={"model": "test-model"}
        )
        
        assert checkpoint_file is not None
        assert Path(checkpoint_file).exists()
        
        # Load checkpoint
        checkpoint_data = manager.load_checkpoint(checkpoint_file)
        assert checkpoint_data is not None
        assert checkpoint_data["evaluation_id"] == "test-eval-001"
        assert len(checkpoint_data["completed_tasks"]) == 2
        assert "task-1" in checkpoint_data["completed_tasks"]
        
        # Verify hash
        assert "checkpoint_hash" in checkpoint_data
        
        print("✅ Checkpoint creation and loading test passed")


def test_checkpoint_integrity():
    """Test checkpoint integrity verification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_dir = Path(tmpdir) / "checkpoints"
        manager = CheckpointManager(checkpoint_dir)
        
        # Create checkpoint
        checkpoint_file = manager.create_checkpoint(
            evaluation_id="test-eval-002",
            completed_tasks=["task-1"],
            results={},
            metadata={}
        )
        
        # Load should succeed
        data1 = manager.load_checkpoint(checkpoint_file)
        assert data1 is not None
        
        # Corrupt checkpoint file
        with open(checkpoint_file, 'w') as f:
            f.write("corrupted data")
        
        # Load should fail integrity check
        data2 = manager.load_checkpoint(checkpoint_file)
        assert data2 is None
        
        print("✅ Checkpoint integrity verification test passed")


def test_evaluation_hash():
    """Test evaluation hash generation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tasks_file = Path(tmpdir) / "tasks.json"
        tasks_file.write_text('{"tasks": []}')
        
        hash1 = generate_evaluation_hash(
            model_name="test-model",
            tasks_file=tasks_file,
            config={"setting": "value1"}
        )
        
        hash2 = generate_evaluation_hash(
            model_name="test-model",
            tasks_file=tasks_file,
            config={"setting": "value1"}
        )
        
        # Same config should produce same hash
        assert hash1 == hash2
        
        # Different config should produce different hash
        hash3 = generate_evaluation_hash(
            model_name="test-model",
            tasks_file=tasks_file,
            config={"setting": "value2"}
        )
        
        assert hash1 != hash3
        
        print("✅ Evaluation hash generation test passed")


if __name__ == "__main__":
    test_checkpoint_creation()
    test_checkpoint_integrity()
    test_evaluation_hash()
    print("\n✅ All checkpoint tests passed!")
