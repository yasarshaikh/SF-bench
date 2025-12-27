"""
Solution loader utilities for loading AI agent solutions from files.
"""
from pathlib import Path
from typing import Dict, Optional
import json


class SolutionLoader:
    """Loads solutions from file-based storage."""
    
    @staticmethod
    def load_from_directory(solution_dir: Path) -> Dict[str, str]:
        """
        Load solutions from a directory structure.
        
        Expected structure:
        solutions/
          sf-apex-001.patch
          sf-apex-002.patch
          sf-lwc-001.patch
        """
        solutions = {}
        
        if not solution_dir.exists():
            return solutions
        
        # Look for .patch files
        for patch_file in solution_dir.glob("*.patch"):
            task_id = patch_file.stem
            try:
                with open(patch_file, 'r') as f:
                    solutions[task_id] = f.read()
            except Exception as e:
                print(f"Warning: Failed to load solution for {task_id}: {str(e)}")
        
        # Also look for .diff files
        for diff_file in solution_dir.glob("*.diff"):
            task_id = diff_file.stem
            if task_id not in solutions:  # Don't override .patch files
                try:
                    with open(diff_file, 'r') as f:
                        solutions[task_id] = f.read()
                except Exception as e:
                    print(f"Warning: Failed to load solution for {task_id}: {str(e)}")
        
        return solutions
    
    @staticmethod
    def load_from_json(solution_file: Path) -> Dict[str, str]:
        """
        Load solutions from a JSON file.
        
        Expected format:
        {
          "sf-apex-001": "diff --git a/...",
          "sf-apex-002": "diff --git a/..."
        }
        """
        solutions = {}
        
        if not solution_file.exists():
            return solutions
        
        try:
            with open(solution_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    solutions = data
                else:
                    print(f"Warning: Expected JSON object, got {type(data)}")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in solution file: {str(e)}")
        except Exception as e:
            print(f"Error: Failed to load solution file: {str(e)}")
        
        return solutions
    
    @staticmethod
    def load_solutions(solution_path: Optional[Path]) -> Dict[str, str]:
        """
        Load solutions from a path (directory or JSON file).
        
        Args:
            solution_path: Path to solution directory or JSON file
            
        Returns:
            Dictionary mapping task_id to patch/diff string
        """
        if not solution_path:
            return {}
        
        solution_path = Path(solution_path)
        
        if solution_path.is_file():
            return SolutionLoader.load_from_json(solution_path)
        elif solution_path.is_dir():
            return SolutionLoader.load_from_directory(solution_path)
        else:
            print(f"Warning: Solution path does not exist: {solution_path}")
            return {}

