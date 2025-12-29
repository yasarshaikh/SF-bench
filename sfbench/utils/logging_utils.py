"""
Log Organization Utilities

Organizes logs in hierarchical structure inspired by SWE-bench:
logs/
└── run_evaluation/
    └── <run_id>/
        └── <model_name>/
            └── <instance_id>/
                ├── run_instance.log
                ├── scratch_org.log
                ├── deployment.log
                ├── test_output.txt
                └── functional_validation.log
"""

import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime


class LogManager:
    """Manages organized log files for evaluations."""
    
    def __init__(self, base_dir: Path = Path("logs")):
        """
        Initialize log manager.
        
        Args:
            base_dir: Base directory for logs (default: logs/)
        """
        self.base_dir = base_dir
        self.run_evaluation_dir = base_dir / "run_evaluation"
        self.run_evaluation_dir.mkdir(parents=True, exist_ok=True)
    
    def get_run_dir(self, run_id: str) -> Path:
        """Get directory for a specific run."""
        run_dir = self.run_evaluation_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir
    
    def get_instance_log_dir(
        self,
        run_id: str,
        model_name: str,
        instance_id: str
    ) -> Path:
        """
        Get log directory for a specific instance.
        
        Structure: logs/run_evaluation/<run_id>/<model_name>/<instance_id>/
        """
        instance_dir = (
            self.run_evaluation_dir / run_id / model_name / instance_id
        )
        instance_dir.mkdir(parents=True, exist_ok=True)
        return instance_dir
    
    def get_log_paths(
        self,
        run_id: str,
        model_name: str,
        instance_id: str
    ) -> Dict[str, str]:
        """
        Get all log file paths for an instance.
        
        Returns:
            Dictionary mapping log type to file path
        """
        instance_dir = self.get_instance_log_dir(run_id, model_name, instance_id)
        
        return {
            "run_instance": str(instance_dir / "run_instance.log"),
            "scratch_org": str(instance_dir / "scratch_org.log"),
            "deployment": str(instance_dir / "deployment.log"),
            "test_output": str(instance_dir / "test_output.txt"),
            "functional_validation": str(instance_dir / "functional_validation.log"),
        }
    
    def write_log(
        self,
        run_id: str,
        model_name: str,
        instance_id: str,
        log_type: str,
        content: str,
        append: bool = True
    ) -> str:
        """
        Write log content to organized log file.
        
        Args:
            run_id: Evaluation run ID
            model_name: Model name
            instance_id: Task instance ID
            log_type: Type of log (run_instance, scratch_org, deployment, etc.)
            content: Log content to write
            append: Append to existing file (default: True)
        
        Returns:
            Path to log file
        """
        log_paths = self.get_log_paths(run_id, model_name, instance_id)
        
        if log_type not in log_paths:
            # Default to run_instance.log
            log_path = log_paths["run_instance"]
        else:
            log_path = log_paths[log_type]
        
        mode = 'a' if append else 'w'
        with open(log_path, mode) as f:
            f.write(content)
            if not content.endswith('\n'):
                f.write('\n')
        
        return log_path
    
    def get_relative_log_path(
        self,
        run_id: str,
        model_name: str,
        instance_id: str,
        log_type: str = "run_instance"
    ) -> str:
        """
        Get relative path to log file (for use in result schema).
        
        Returns:
            Relative path like "logs/run_evaluation/<run_id>/<model>/<instance>/run_instance.log"
        """
        log_paths = self.get_log_paths(run_id, model_name, instance_id)
        log_path = log_paths.get(log_type, log_paths["run_instance"])
        
        # Return relative to project root
        try:
            return str(Path(log_path).relative_to(Path.cwd()))
        except ValueError:
            # If not relative, return absolute path
            return log_path


# Global log manager instance
_log_manager = None

def get_log_manager(base_dir: Optional[Path] = None) -> LogManager:
    """Get or create global log manager instance."""
    global _log_manager
    if _log_manager is None or base_dir is not None:
        _log_manager = LogManager(base_dir or Path("logs"))
    return _log_manager
