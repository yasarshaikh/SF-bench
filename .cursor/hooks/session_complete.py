#!/usr/bin/env python3
"""
Session completion hook for SF-Bench.

Logs session completion and triggers memory bank updates for significant changes.
Communicates via JSON over stdio.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
MEMORY_BANK = PROJECT_ROOT / ".cursor" / "memory-bank"
LOGS_DIR = PROJECT_ROOT / "logs" / "cursor_sessions"


def is_significant_change(edited_files: list) -> bool:
    """
    Determine if changes warrant memory bank update.

    Args:
        edited_files: List of files edited in the session.

    Returns:
        True if changes are significant.
    """
    if len(edited_files) >= 3:
        return True

    # Core modules that warrant tracking
    core_patterns = [
        "sfbench/engine.py",
        "sfbench/main.py",
        "sfbench/config.py",
        "sfbench/runners/",
        "sfbench/utils/",
        "sfbench/validators/",
        ".cursor/",
        "AGENTS.md",
    ]

    for file_path in edited_files:
        for pattern in core_patterns:
            if pattern in str(file_path):
                return True

    return False


def log_session(payload: dict) -> Path:
    """
    Log session completion to audit trail.

    Args:
        payload: Session metadata from Cursor.

    Returns:
        Path to the log file created.
    """
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    session_id = payload.get("session_id", f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    timestamp = datetime.now().isoformat()
    edited_files = payload.get("edited_files", [])

    log_entry = {
        "session_id": session_id,
        "timestamp": timestamp,
        "edited_files": edited_files,
        "files_count": len(edited_files),
        "significant_change": is_significant_change(edited_files),
    }

    log_file = LOGS_DIR / f"{session_id}.json"
    log_file.write_text(json.dumps(log_entry, indent=2))

    return log_file


def append_to_active_context(message: str):
    """
    Append a note to activeContext.md about session completion.

    Args:
        message: Message to append to recent changes.
    """
    active_context = MEMORY_BANK / "activeContext.md"

    if not active_context.exists():
        return

    content = active_context.read_text()

    # Find "## Recent Changes" section and add entry
    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"- [{today}] {message}\n"

    if "## Recent Changes" in content:
        # Insert after the header
        parts = content.split("## Recent Changes")
        if len(parts) == 2:
            header, rest = parts
            # Find the first line after the header
            lines = rest.split("\n", 2)
            if len(lines) >= 2:
                updated = f"{header}## Recent Changes\n{new_entry}{lines[1]}\n{lines[2] if len(lines) > 2 else ''}"
                active_context.write_text(updated)


def main():
    """Main entry point for the hook."""
    try:
        # Read hook payload from stdin
        payload = json.load(sys.stdin)
        edited_files = payload.get("edited_files", [])

        # Log session
        log_file = log_session(payload)

        # Check if significant change
        significant = is_significant_change(edited_files)

        # Update memory bank for significant changes
        if significant and edited_files:
            # Create a brief summary
            summary = f"Session completed: {len(edited_files)} files modified"
            append_to_active_context(summary)

        print(
            json.dumps(
                {
                    "success": True,
                    "logged": True,
                    "log_file": str(log_file),
                    "significant_change": significant,
                    "files_edited": len(edited_files),
                }
            )
        )

    except json.JSONDecodeError:
        print(json.dumps({"success": False, "error": "Invalid JSON input"}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


if __name__ == "__main__":
    main()
