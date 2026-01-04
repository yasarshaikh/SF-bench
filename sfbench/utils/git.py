import subprocess
import shutil
from pathlib import Path
from typing import Optional


class GitError(Exception):
    pass


def clone_repository(repo_url: str, target_dir: Path, timeout: int = 300) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        result = subprocess.run(
            ['git', 'clone', repo_url, str(target_dir)],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise GitError(f"Failed to clone repository: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        raise GitError(f"Git clone timed out after {timeout} seconds")
    except Exception as e:
        raise GitError(f"Unexpected error cloning repository: {str(e)}")


def checkout_commit(repo_dir: Path, commit_hash: str, timeout: int = 60) -> None:
    try:
        result = subprocess.run(
            ['git', 'checkout', commit_hash],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise GitError(f"Failed to checkout commit {commit_hash}: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        raise GitError(f"Git checkout timed out after {timeout} seconds")
    except Exception as e:
        raise GitError(f"Unexpected error checking out commit: {str(e)}")


def apply_patch(repo_dir: Path, patch_diff: str, timeout: int = 60) -> None:
    """
    Apply a patch to a repository using multiple fallback strategies (inspired by SWE-bench).
    
    This function validates patches before applying and tries multiple patch application methods
    in sequence, giving models a fair chance even if their patches have minor formatting issues.
    Only fails if ALL strategies fail.
    
    Strategies (in order):
    1. git apply --check (validation only)
    2. git apply --whitespace=fix --ignore-whitespace (strict)
    3. git apply --whitespace=fix --ignore-whitespace --reject (allows partial)
    4. git apply --3way --whitespace=fix (3-way merge for context mismatches)
    5. patch --batch --fuzz=5 -p1 (fuzzy matching, SWE-bench fallback)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Validate patch is not empty
    if not patch_diff or not patch_diff.strip():
        raise GitError("Cannot apply empty patch")
    
    # Clean the patch before applying
    cleaned_patch = _clean_patch(patch_diff)
    
    # Validate cleaned patch is not empty
    if not cleaned_patch or not cleaned_patch.strip():
        raise GitError("Patch is empty after cleaning")
    
    # Check if patch has valid diff format (at least one line starting with +, -, or @@)
    has_diff_content = any(
        line.startswith(('+', '-', '@@')) and not line.startswith('+++') and not line.startswith('---')
        for line in cleaned_patch.split('\n')
    )
    if not has_diff_content:
        raise GitError("Patch does not contain valid diff content")
    
    # VALIDATION PIPELINE: Check patch validity before applying
    try:
        check_result = subprocess.run(
            ['git', 'apply', '--check', '--whitespace=fix', '--ignore-whitespace'],
            input=cleaned_patch,
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if check_result.returncode == 0:
            logger.debug("Patch validation passed: git apply --check succeeded")
        else:
            logger.warning(f"Patch validation warning (will try fallback strategies): {check_result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        logger.warning("Patch validation timed out (will try fallback strategies)")
    except Exception as e:
        logger.warning(f"Patch validation error (will try fallback strategies): {str(e)}")
    
    # Multi-strategy patch application (inspired by SWE-bench)
    strategies = [
        {
            "name": "git_apply_strict",
            "cmd": ['git', 'apply', '--whitespace=fix', '--ignore-whitespace'],
            "use_stdin": True
        },
        {
            "name": "git_apply_reject",
            "cmd": ['git', 'apply', '--whitespace=fix', '--ignore-whitespace', '--reject'],
            "use_stdin": True
        },
        {
            "name": "git_apply_3way",
            "cmd": ['git', 'apply', '--3way', '--whitespace=fix'],
            "use_stdin": True
        },
        {
            "name": "patch_fuzzy",
            "cmd": ['patch', '--batch', '--fuzz=5', '-p1'],
            "use_stdin": True,
            "requires_patch_file": False  # patch command can use stdin
        }
    ]
    
    last_error = None
    for strategy in strategies:
        try:
            if strategy["use_stdin"]:
                result = subprocess.run(
                    strategy["cmd"],
                    input=cleaned_patch,
                    cwd=str(repo_dir),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                # For strategies that need file input (future use)
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
                    f.write(cleaned_patch)
                    patch_file = f.name
                
                try:
                    result = subprocess.run(
                        strategy["cmd"] + [patch_file],
                        cwd=str(repo_dir),
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                finally:
                    import os
                    os.unlink(patch_file)
            
            if result.returncode == 0:
                # Success! Log which strategy worked (for debugging)
                if strategy["name"] != "git_apply_strict":
                    print(f"⚠️  Patch applied using fallback strategy: {strategy['name']}")
                return  # Success
            
            # Store error for final reporting
            last_error = result.stderr or result.stdout or f"Exit code: {result.returncode}"
            
        except subprocess.TimeoutExpired:
            last_error = f"Strategy {strategy['name']} timed out after {timeout} seconds"
            continue
        except Exception as e:
            last_error = f"Strategy {strategy['name']} failed: {str(e)}"
            continue
    
    # All strategies failed
    error_msg = f"Failed to apply patch after trying {len(strategies)} strategies"
    if last_error:
        error_msg += f". Last error: {last_error[:500]}"  # Limit error message length
    raise GitError(error_msg)


def _clean_patch(patch_diff: str) -> str:
    """
    Clean patch content to handle common formatting issues from AI models.
    
    Handles:
    - Markdown code fences
    - Malformed diff lines (lines starting with + or - but invalid)
    - Empty lines in diff context
    - Trailing whitespace
    - Incomplete patch lines
    - Multiple diff headers (extract first complete diff)
    - Embedded text/explanations in patches
    - Truncated patches
    """
    lines = patch_diff.split('\n')
    cleaned_lines = []
    in_diff = False
    last_was_hunk_header = False
    diff_count = 0
    seen_first_diff = False
    
    for i, line in enumerate(lines):
        # Remove markdown code fences if present
        if line.strip().startswith('```'):
            continue
        
        # Detect new diff header - if we've already seen one, skip subsequent ones
        # (AI models sometimes include multiple diffs or explanations)
        if line.startswith('diff --git'):
            diff_count += 1
            if diff_count > 1:
                # Multiple diff headers detected - stop at first complete diff
                # This handles cases where AI includes explanations or multiple patches
                break
            in_diff = True
            last_was_hunk_header = False
            seen_first_diff = True
            cleaned_lines.append(line.rstrip())
            continue
        
        # Start collecting when we see diff header components
        if not seen_first_diff and (line.startswith('---') or line.startswith('+++')):
            in_diff = True
            last_was_hunk_header = False
            seen_first_diff = True
        
        if in_diff:
            # Handle file headers (--- and +++)
            if line.startswith('---') or line.startswith('+++'):
                cleaned_lines.append(line.rstrip())
                last_was_hunk_header = False
                continue
            
            # Handle hunk headers (@@ ... @@)
            if line.startswith('@@'):
                cleaned_lines.append(line.rstrip())
                last_was_hunk_header = True
                continue
            
            # Handle diff content lines
            if line.startswith(' ') or line.startswith('-') or line.startswith('+'):
                # For diff lines, preserve the leading character but clean trailing whitespace
                cleaned_line = line.rstrip()
                
                # Fix malformed lines: if line is just "+" or "-" or "+ " or "- ", skip it
                # (these cause "malformed patch" errors)
                if cleaned_line in ('+', '-', '+ ', '- '):
                    # Skip malformed single-character lines
                    continue
                
                # Fix lines that are just whitespace after + or -
                if len(cleaned_line) == 1 and cleaned_line in ('+', '-'):
                    continue
                
                # Skip lines that look like instructions/explanations (not code)
                # e.g., "+5. Deploy LWC bundle" - these are explanations, not code
                if cleaned_line.startswith(('+', '-')) and len(cleaned_line) > 1:
                    # Check if it looks like an instruction (starts with number, bullet, etc.)
                    rest = cleaned_line[1:].strip()
                    if rest and (rest[0].isdigit() or rest.startswith(('. ', '- ', '* '))):
                        # Likely an instruction, not code - skip it
                        continue
                
                if cleaned_line:  # Don't add empty lines
                    cleaned_lines.append(cleaned_line)
                last_was_hunk_header = False
            elif line.startswith('\\'):
                # Handle "No newline at end of file" markers
                cleaned_lines.append(line.rstrip())
                last_was_hunk_header = False
            else:
                # For non-diff lines (headers, etc.), just strip trailing whitespace
                # But skip empty lines right after hunk headers (common malformation)
                if last_was_hunk_header and not line.strip():
                    continue
                
                # Skip lines that look like explanations or instructions (not diff content)
                # These often appear in AI-generated patches
                stripped = line.strip()
                if stripped and not stripped.startswith(('index', 'new file', 'deleted file', 'similarity', 'rename')):
                    # If it doesn't look like a valid diff metadata line, skip it
                    # (unless we're in a valid diff context)
                    if not (stripped.startswith('diff') or stripped.startswith('---') or stripped.startswith('+++')):
                        continue
                
                cleaned_lines.append(line.rstrip())
                last_was_hunk_header = False
        else:
            # Before diff starts, skip instructions/explanations
            # Only keep if it looks like it might be part of a diff
            if line.startswith(('diff', '---', '+++', '@@', 'index')):
                cleaned_lines.append(line)
    
    # Final pass: remove any remaining malformed lines
    final_lines = []
    for i, line in enumerate(cleaned_lines):
        # Skip standalone + or - lines that aren't part of valid diff
        if line in ('+', '-') and i > 0:
            prev_line = final_lines[-1] if final_lines else ''
            # If previous line doesn't look like diff context, skip this malformed line
            if not (prev_line.startswith((' ', '+', '-', '@@', 'diff', '---', '+++'))):
                continue
        final_lines.append(line)
    
    result = '\n'.join(final_lines)
    
    # Ensure result ends with newline (required by some patch tools)
    if result and not result.endswith('\n'):
        result += '\n'
    
    return result
