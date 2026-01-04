"""
Checkpoint and Resume functionality for evaluations.

Allows evaluations to be paused and resumed, preventing loss of progress
on long-running evaluations.
"""
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manages checkpoints for evaluation runs."""
    
    def __init__(self, checkpoint_dir: Path):
        """
        Initialize checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.current_checkpoint: Optional[str] = None
    
    def create_checkpoint(
        self,
        evaluation_id: str,
        completed_tasks: List[str],
        results: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a checkpoint for the current evaluation state.
        
        Args:
            evaluation_id: Unique identifier for this evaluation
            completed_tasks: List of task IDs that have been completed
            results: Results dictionary for completed tasks
            metadata: Additional metadata to store
            
        Returns:
            Checkpoint file path
        """
        checkpoint_data = {
            "evaluation_id": evaluation_id,
            "timestamp": datetime.now().isoformat(),
            "completed_tasks": completed_tasks,
            "results": results,
            "metadata": metadata or {}
        }
        
        # Create checkpoint file with hash for verification
        checkpoint_file = self.checkpoint_dir / f"{evaluation_id}_checkpoint.json"
        hash_file = self.checkpoint_dir / f"{evaluation_id}_checkpoint.sha256"
        
        # Calculate hash BEFORE adding hash field (to avoid circular dependency)
        checkpoint_content_no_hash = json.dumps(checkpoint_data, indent=2, sort_keys=True)
        checkpoint_hash = hashlib.sha256(checkpoint_content_no_hash.encode()).hexdigest()
        
        # Add hash to data
        checkpoint_data["checkpoint_hash"] = checkpoint_hash
        checkpoint_content = json.dumps(checkpoint_data, indent=2, sort_keys=True)
        
        checkpoint_file.write_text(checkpoint_content)
        hash_file.write_text(checkpoint_hash)
        
        self.current_checkpoint = str(checkpoint_file)
        logger.info(f"Checkpoint created: {checkpoint_file} (hash: {checkpoint_hash[:16]}...)")
        
        return str(checkpoint_file)
    
    def load_checkpoint(self, checkpoint_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load a checkpoint from file.
        
        Args:
            checkpoint_file: Path to checkpoint file. If None, uses current checkpoint.
            
        Returns:
            Checkpoint data dictionary or None if not found/invalid
        """
        if checkpoint_file is None:
            checkpoint_file = self.current_checkpoint
        
        if checkpoint_file is None:
            return None
        
        checkpoint_path = Path(checkpoint_file)
        if not checkpoint_path.exists():
            logger.warning(f"Checkpoint file not found: {checkpoint_file}")
            return None
        
        try:
            checkpoint_data = json.loads(checkpoint_path.read_text())
            
            # Verify checkpoint integrity
            stored_hash = checkpoint_data.get("checkpoint_hash")
            if stored_hash:
                # Recalculate hash (excluding the hash field itself)
                checkpoint_data_no_hash = {k: v for k, v in checkpoint_data.items() if k != "checkpoint_hash"}
                checkpoint_content = json.dumps(checkpoint_data_no_hash, indent=2, sort_keys=True)
                calculated_hash = hashlib.sha256(checkpoint_content.encode()).hexdigest()
                
                if calculated_hash != stored_hash:
                    logger.error(f"Checkpoint integrity check failed: hash mismatch")
                    return None
            
            logger.info(f"Checkpoint loaded: {checkpoint_file} (evaluation: {checkpoint_data.get('evaluation_id')})")
            return checkpoint_data
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {str(e)}")
            return None
    
    def get_completed_tasks(self, checkpoint_file: Optional[str] = None) -> List[str]:
        """
        Get list of completed task IDs from checkpoint.
        
        Args:
            checkpoint_file: Path to checkpoint file
            
        Returns:
            List of completed task IDs
        """
        checkpoint = self.load_checkpoint(checkpoint_file)
        if checkpoint:
            return checkpoint.get("completed_tasks", [])
        return []
    
    def get_results(self, checkpoint_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Get results dictionary from checkpoint.
        
        Args:
            checkpoint_file: Path to checkpoint file
            
        Returns:
            Results dictionary
        """
        checkpoint = self.load_checkpoint(checkpoint_file)
        if checkpoint:
            return checkpoint.get("results", {})
        return {}
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint metadata dictionaries
        """
        checkpoints = []
        for checkpoint_file in self.checkpoint_dir.glob("*_checkpoint.json"):
            try:
                data = json.loads(checkpoint_file.read_text())
                checkpoints.append({
                    "file": str(checkpoint_file),
                    "evaluation_id": data.get("evaluation_id"),
                    "timestamp": data.get("timestamp"),
                    "completed_count": len(data.get("completed_tasks", []))
                })
            except Exception:
                continue
        
        return sorted(checkpoints, key=lambda x: x.get("timestamp", ""), reverse=True)


def generate_evaluation_hash(
    model_name: str,
    tasks_file: Path,
    config: Dict[str, Any]
) -> str:
    """
    Generate a unique hash for an evaluation run.
    
    This hash can be used to verify that results match the exact evaluation configuration.
    
    Args:
        model_name: Name of the model being evaluated
        tasks_file: Path to tasks file
        config: Evaluation configuration dictionary
        
    Returns:
        SHA-256 hash as hexadecimal string
    """
    # Include all relevant configuration in hash
    hash_input = {
        "model_name": model_name,
        "tasks_file": str(tasks_file),
        "tasks_file_hash": hashlib.sha256(tasks_file.read_bytes()).hexdigest() if tasks_file.exists() else "",
        "config": config
    }
    
    hash_content = json.dumps(hash_input, sort_keys=True)
    return hashlib.sha256(hash_content.encode()).hexdigest()
