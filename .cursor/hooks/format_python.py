#!/usr/bin/env python3
"""
Auto-format Python files after Cursor edits.

Formats files using Black and isort according to SF-Bench standards.
Communicates via JSON over stdio.
"""
import json
import subprocess
import sys
from pathlib import Path


def format_file(file_path: Path) -> dict:
    """
    Format a Python file using Black and isort.

    Args:
        file_path: Path to the Python file to format.

    Returns:
        Dict with success status and details.
    """
    if not file_path.exists():
        return {"success": False, "error": "File not found", "skipped": False}

    try:
        # Run isort first (import sorting)
        subprocess.run(
            ["isort", "--profile", "black", "--line-length", "100", str(file_path)],
            check=True,
            capture_output=True,
            timeout=30,
        )

        # Run black (code formatting)
        subprocess.run(
            ["black", "--line-length", "100", "--quiet", str(file_path)],
            check=True,
            capture_output=True,
            timeout=30,
        )

        return {"success": True, "formatted": True, "skipped": False}

    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Formatting failed: {e.stderr.decode() if e.stderr else str(e)}",
            "skipped": False,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Formatting timed out", "skipped": False}
    except FileNotFoundError as e:
        # Tool not installed - skip gracefully
        return {"success": True, "skipped": True, "reason": f"Tool not found: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e), "skipped": False}


def main():
    """Main entry point for the hook."""
    try:
        # Read hook payload from stdin
        payload = json.load(sys.stdin)
        file_path = Path(payload.get("file_path", ""))

        # Only format Python files
        if file_path.suffix != ".py":
            print(json.dumps({"success": True, "skipped": True, "reason": "Not a Python file"}))
            return

        # Skip files in excluded directories
        excluded_dirs = ["workspace", "results", "logs", ".pytest_cache", "__pycache__", "venv"]
        for excluded in excluded_dirs:
            if excluded in str(file_path):
                print(
                    json.dumps(
                        {"success": True, "skipped": True, "reason": f"In excluded dir: {excluded}"}
                    )
                )
                return

        result = format_file(file_path)
        print(json.dumps(result))

    except json.JSONDecodeError:
        print(json.dumps({"success": False, "error": "Invalid JSON input"}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


if __name__ == "__main__":
    main()
