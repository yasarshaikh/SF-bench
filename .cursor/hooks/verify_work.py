#!/usr/bin/env python3
"""
Work Verification Hook for SF-Bench.

This hook runs after task completion to verify work quality.
Acts as a "judge" that validates changes before they're considered done.

Inspired by Boris Cherny's verification pattern:
"The most important thing to get great results — give Claude a way to verify its work."
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent
REPORT_DIR = PROJECT_ROOT / ".cursor" / "verification-reports"


def check_no_secrets(files: List[str]) -> Tuple[bool, List[str]]:
    """
    Scan files for potential secrets.

    Returns:
        Tuple of (passed, list of violations)
    """
    secret_patterns = [
        ("API key pattern", r"['\"](?:sk-|pk-|api[_-]?key)[a-zA-Z0-9]{20,}['\"]"),
        ("AWS key pattern", r"AKIA[0-9A-Z]{16}"),
        ("Generic secret", r"(?:password|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]"),
        ("Private key", r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----"),
    ]

    violations = []

    for file_path in files:
        if not Path(file_path).exists():
            continue

        try:
            content = Path(file_path).read_text()
            for name, pattern in secret_patterns:
                import re

                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(f"{file_path}: Potential {name} detected")
        except Exception:
            continue

    return len(violations) == 0, violations


def check_no_debug_prints(files: List[str]) -> Tuple[bool, List[str]]:
    """
    Check for debug prints left in code.

    Returns:
        Tuple of (passed, list of violations)
    """
    debug_patterns = [
        r"^\s*print\s*\(",  # print statements
        r"^\s*console\.log\s*\(",  # JS console.log
        r"^\s*debugger\s*;?$",  # debugger statements
        r"# ?DEBUG",  # DEBUG comments
        r"# ?TODO(?!:)",  # TODO without issue reference
    ]

    violations = []

    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            continue
        if path.suffix not in [".py", ".js", ".ts", ".apex", ".cls"]:
            continue

        try:
            import re

            for i, line in enumerate(path.read_text().splitlines(), 1):
                for pattern in debug_patterns:
                    if re.search(pattern, line):
                        # Skip if in test file
                        if "test" in file_path.lower():
                            continue
                        violations.append(f"{file_path}:{i}: {line.strip()[:50]}")
        except Exception:
            continue

    return len(violations) == 0, violations


def check_no_profanity(files: List[str]) -> Tuple[bool, List[str]]:
    """
    Check for inappropriate language using word boundaries.

    Returns:
        Tuple of (passed, list of violations)
    """
    import re

    # Words that should not appear as standalone words
    inappropriate = [
        r"\bfuck\b",
        r"\bshit\b",
        r"\bdamn\b",
        r"\bcrap\b",
        r"\bbastard\b",
        r"\bidiot\b",
    ]

    violations = []

    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            continue

        try:
            content = path.read_text().lower()
            for pattern in inappropriate:
                if re.search(pattern, content):
                    word = pattern.replace(r"\b", "")
                    violations.append(f"{file_path}: Contains '{word}'")
        except Exception:
            continue

    return len(violations) == 0, violations


def check_tests_pass() -> Tuple[bool, str]:
    """
    Run pytest and check if tests pass.

    Returns:
        Tuple of (passed, output message)
    """
    try:
        result = subprocess.run(
            ["pytest", "--tb=short", "-q"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            return True, "All tests passed"
        else:
            return False, f"Tests failed:\n{result.stdout}\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "Tests timed out after 5 minutes"
    except FileNotFoundError:
        return True, "pytest not found - skipping test verification"
    except Exception as e:
        return False, f"Test execution error: {e}"


def check_linting(files: List[str]) -> Tuple[bool, List[str]]:
    """
    Check for linting violations in changed files.

    Returns:
        Tuple of (passed, list of violations)
    """
    python_files = [f for f in files if f.endswith(".py")]

    if not python_files:
        return True, []

    try:
        result = subprocess.run(
            ["flake8", "--max-line-length=100", "--select=E,F,W"] + python_files,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

        violations = [line for line in result.stdout.splitlines() if line.strip()]
        return len(violations) == 0, violations

    except FileNotFoundError:
        return True, []  # flake8 not installed
    except Exception:
        return True, []


def run_verification(edited_files: List[str]) -> Dict:
    """
    Run all verification checks.

    Args:
        edited_files: List of files that were edited.

    Returns:
        Verification report as dict.
    """
    report = {
        "passed": True,
        "checks": [],
        "files_checked": len(edited_files),
    }

    # Check 1: No secrets
    passed, violations = check_no_secrets(edited_files)
    report["checks"].append(
        {
            "name": "No Secrets",
            "passed": passed,
            "critical": True,
            "violations": violations[:5],  # Limit output
        }
    )
    if not passed:
        report["passed"] = False

    # Check 2: No debug prints
    passed, violations = check_no_debug_prints(edited_files)
    report["checks"].append(
        {
            "name": "No Debug Artifacts",
            "passed": passed,
            "critical": False,
            "violations": violations[:5],
        }
    )

    # Check 3: No profanity
    passed, violations = check_no_profanity(edited_files)
    report["checks"].append(
        {
            "name": "Professional Language",
            "passed": passed,
            "critical": True,
            "violations": violations[:5],
        }
    )
    if not passed:
        report["passed"] = False

    # Check 4: Linting
    passed, violations = check_linting(edited_files)
    report["checks"].append(
        {"name": "Linting", "passed": passed, "critical": False, "violations": violations[:10]}
    )

    # Check 5: Tests (only if significant changes)
    if len(edited_files) >= 3 or any("sfbench/" in f for f in edited_files):
        passed, message = check_tests_pass()
        report["checks"].append(
            {"name": "Tests", "passed": passed, "critical": True, "message": message[:500]}
        )
        if not passed:
            report["passed"] = False

    return report


def save_report(report: Dict) -> Path:
    """Save verification report to file."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_file = REPORT_DIR / f"verify-{timestamp}.json"

    report_file.write_text(json.dumps(report, indent=2))
    return report_file


def format_report(report: Dict) -> str:
    """Format report for display."""
    lines = []

    overall = "✅ PASSED" if report["passed"] else "❌ FAILED"
    lines.append(f"\n{'='*50}")
    lines.append(f"VERIFICATION REPORT: {overall}")
    lines.append(f"Files checked: {report['files_checked']}")
    lines.append(f"{'='*50}\n")

    for check in report["checks"]:
        status = "✅" if check["passed"] else ("❌" if check.get("critical") else "⚠️")
        lines.append(f"{status} {check['name']}")

        if not check["passed"]:
            if "violations" in check:
                for v in check["violations"]:
                    lines.append(f"   → {v}")
            if "message" in check:
                lines.append(f"   → {check['message'][:200]}")

    lines.append("")
    return "\n".join(lines)


def main():
    """Main entry point for the hook."""
    try:
        # Read hook payload from stdin
        payload = json.load(sys.stdin)
        edited_files = payload.get("edited_files", [])

        if not edited_files:
            print(json.dumps({"success": True, "skipped": True, "reason": "No files to verify"}))
            return

        # Run verification
        report = run_verification(edited_files)

        # Save report
        report_file = save_report(report)

        # Output formatted report to stderr (for visibility)
        print(format_report(report), file=sys.stderr)

        # Return JSON result
        print(
            json.dumps(
                {
                    "success": report["passed"],
                    "report_file": str(report_file),
                    "checks_passed": sum(1 for c in report["checks"] if c["passed"]),
                    "checks_total": len(report["checks"]),
                    "critical_failures": [
                        c["name"] for c in report["checks"] if not c["passed"] and c.get("critical")
                    ],
                }
            )
        )

    except json.JSONDecodeError:
        print(json.dumps({"success": False, "error": "Invalid JSON input"}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


if __name__ == "__main__":
    main()
