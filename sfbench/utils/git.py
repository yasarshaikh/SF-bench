import subprocess
import shutil
from pathlib import Path
from typing import Optional
from sfbench.config import get_config


class GitError(Exception):
    """Base exception for Git operations."""
    pass


class PatchApplicationError(GitError):
    """
    Exception for patch application failures that should be treated as model failures (FAIL),
    not tool errors (ERROR).
    
    This is raised when:
    - Patch is corrupt/malformed (model generated invalid patch)
    - Patch is incomplete/truncated (model didn't complete the patch)
    - Patch structure is invalid (model didn't follow diff format)
    
    These are model limitations, not tool bugs.
    """
    pass


def clone_repository(repo_url: str, target_dir: Path, timeout: Optional[int] = None) -> None:
    """Clone a repository with configurable timeout."""
    if timeout is None:
        timeout = get_config().timeout_git
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


def checkout_commit(repo_dir: Path, commit_hash: str, timeout: Optional[int] = None) -> None:
    """Checkout a commit with configurable timeout."""
    if timeout is None:
        timeout = get_config().timeout_git
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


def apply_patch(repo_dir: Path, patch_diff: str, timeout: Optional[int] = None) -> None:
    """Apply a patch with configurable timeout."""
    if timeout is None:
        timeout = get_config().timeout_patch
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
    try:
        cleaned_patch = _clean_patch(patch_diff)
    except GitError as e:
        # Re-raise GitError from cleaning (e.g., incomplete structure)
        raise
    except Exception as e:
        # Wrap other cleaning errors
        logger.error(f"Patch cleaning failed: {str(e)}")
        raise GitError(f"Patch cleaning failed: {str(e)}")
    
    # Validate cleaned patch is not empty
    if not cleaned_patch or not cleaned_patch.strip():
        raise PatchApplicationError("Patch is empty after cleaning - AI model generated empty or invalid patch")
    
    # Check if patch has valid diff format (at least one line starting with +, -, or @@)
    has_diff_content = any(
        line.startswith(('+', '-', '@@')) and not line.startswith('+++') and not line.startswith('---')
        for line in cleaned_patch.split('\n')
    )
    
    if not has_diff_content:
        raise PatchApplicationError("Patch does not contain valid diff content - AI model did not generate a valid diff")
    
    # VALIDATE PATCH STRUCTURE: Check for complete hunks
    # "unexpected end of file" errors occur when hunks are incomplete (missing context lines)
    patch_lines = cleaned_patch.split('\n')
    hunk_headers = [i for i, line in enumerate(patch_lines) if line.startswith('@@')]
    
    if hunk_headers:
        # Validate each hunk is complete
        for i, hunk_idx in enumerate(hunk_headers):
            # Get hunk end (next hunk header or end of patch)
            hunk_end = hunk_headers[i + 1] if i + 1 < len(hunk_headers) else len(patch_lines)
            hunk_lines = patch_lines[hunk_idx:hunk_end]
            
            # A valid hunk should have:
            # 1. Hunk header (@@ ... @@)
            # 2. At least one context line (starting with space) or diff line (+/-)
            # 3. Should not end abruptly (last line should be context or diff, not empty)
            
            if len(hunk_lines) < 2:
                # Hunk with only header - incomplete
                logger.warning(f"Detected incomplete hunk at line {hunk_idx + 1}: hunk header without content")
                # Try to repair: if this is the last hunk and it's incomplete, remove it
                if i == len(hunk_headers) - 1:
                    logger.info(f"Removing incomplete final hunk (line {hunk_idx + 1})")
                    cleaned_patch = '\n'.join(patch_lines[:hunk_idx])
                    patch_lines = cleaned_patch.split('\n')  # Update for next iteration
                    break
            else:
                # Check if hunk ends properly (last line should be context or diff)
                last_hunk_line = hunk_lines[-1].strip()
                if not last_hunk_line or (not last_hunk_line.startswith((' ', '+', '-', '\\'))):
                    # Hunk ends with empty line or invalid content - might be truncated
                    logger.warning(f"Detected potentially truncated hunk at line {hunk_idx + 1}: last line is '{last_hunk_line[:50] if last_hunk_line else 'empty'}'")
                    # If this is the last hunk, try to repair by removing incomplete trailing lines
                    if i == len(hunk_headers) - 1:
                        # Find last valid diff line
                        last_valid_idx = hunk_idx
                        for j in range(len(hunk_lines) - 1, 0, -1):
                            if hunk_lines[j].strip() and hunk_lines[j].startswith((' ', '+', '-', '\\')):
                                last_valid_idx = hunk_idx + j + 1
                                break
                        if last_valid_idx < len(patch_lines):
                            logger.info(f"Truncating incomplete final hunk: removing lines {last_valid_idx + 1} to {len(patch_lines)}")
                            cleaned_patch = '\n'.join(patch_lines[:last_valid_idx])
                            patch_lines = cleaned_patch.split('\n')  # Update for next iteration
                            break
    
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
            logger.debug(f"Patch validation passed: git apply --check succeeded")
        else:
            # Log at INFO level (not WARNING) since fallback strategies will handle it
            error_preview = check_result.stderr[:200] if check_result.stderr else "Unknown validation error"
            logger.info(f"Patch validation check failed (will try fallback strategies): {error_preview}")
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
                    logger.info(f"Patch applied using fallback strategy: {strategy['name']}")
                else:
                    logger.debug(f"Patch applied successfully using strict strategy")
                return  # Success
            
            # Store error for final reporting
            last_error = result.stderr or result.stdout or f"Exit code: {result.returncode}"
            
        except subprocess.TimeoutExpired:
            last_error = f"Strategy {strategy['name']} timed out after {timeout} seconds"
            continue
        except Exception as e:
            last_error = f"Strategy {strategy['name']} failed: {str(e)}"
            continue
    
    # All strategies failed - log detailed information for debugging
    logger.error(f"All {len(strategies)} patch application strategies failed")
    if last_error:
        logger.error(f"Last strategy error: {last_error[:500]}")
        logger.debug(f"Cleaned patch preview (first 1000 chars): {cleaned_patch[:1000]}")
    
    # Create informative error message
    error_msg = f"Failed to apply patch after trying {len(strategies)} strategies"
    if last_error:
        # Extract key error information without overwhelming the message
        error_preview = last_error[:300] if len(last_error) > 300 else last_error
        error_msg += f". Last error: {error_preview}"
    # FINAL ERROR MESSAGE: Clearly distinguish tool vs model issues
    # If we tried all strategies and failed, it's a model issue (corrupt/incomplete patch)
    # If we had validation errors, it's also a model issue
    error_msg = (
        f"Failed to apply patch after trying 4 strategies. "
        f"Last error: {last_error}\n"
        f"This indicates the AI model generated a corrupt, incomplete, or malformed patch. "
        f"All patch application strategies (strict, reject, 3-way merge, fuzzy) were attempted. "
        f"Patch validation and cleaning were performed, but the patch structure is fundamentally invalid."
    )
    # Raise PatchApplicationError (not GitError) so it can be treated as FAIL, not ERROR
    raise PatchApplicationError(error_msg)


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
    import logging
    logger = logging.getLogger(__name__)
    
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
                    logger.debug(f"Skipping malformed single-character diff line: '{cleaned_line}'")
                    continue
                
                # Fix lines that are just whitespace after + or -
                if len(cleaned_line) == 1 and cleaned_line in ('+', '-'):
                    logger.debug(f"Skipping malformed single-character line: '{cleaned_line}'")
                    continue
                
                # Fix lines that start with + or - but have no actual content (just whitespace)
                if cleaned_line.startswith(('+', '-')) and len(cleaned_line.strip()) <= 1:
                    logger.debug(f"Skipping empty diff line: '{cleaned_line}'")
                    continue
                
                # Fix lines that have + or - but are not valid diff lines (e.g., "+ Here's what to do:")
                # Valid diff lines should have context (space) or actual code after +/-
                if cleaned_line.startswith(('+', '-')) and len(cleaned_line) > 1:
                    rest = cleaned_line[1:].strip()
                    # If rest is empty or looks like prose/instructions, skip
                    if not rest or (len(rest) < 3 and not rest[0].isalnum()):
                        logger.debug(f"Skipping non-code diff line: '{cleaned_line[:50]}'")
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
    
    # VALIDATE PATCH COMPLETENESS: Check for truncated patches
    # "unexpected end of file" errors often occur when patches are cut off mid-hunk
    if result:
        result_lines = result.split('\n')
        
        # Check if patch ends with incomplete hunk
        # Valid patches should end with:
        # - A context line (space)
        # - A diff line (+ or -)
        # - A "No newline" marker (\)
        # - NOT with a hunk header (@@) or file header (---/+++)
        
        if result_lines:
            last_line = result_lines[-1].strip()
            second_last = result_lines[-2].strip() if len(result_lines) > 1 else ''
            
            # If patch ends with hunk header, it's incomplete
            if last_line.startswith('@@'):
                logger.warning("Patch ends with hunk header - removing incomplete final hunk")
                # Remove the incomplete hunk
                for i in range(len(result_lines) - 1, -1, -1):
                    if result_lines[i].startswith('@@'):
                        result_lines = result_lines[:i]
                        break
                result = '\n'.join(result_lines)
            
            # If patch ends with file header (---/+++) without content, it's incomplete
            elif last_line.startswith(('---', '+++')):
                if not second_last or not second_last.startswith((' ', '+', '-', '@@')):
                    logger.warning("Patch ends with file header without content - removing incomplete header")
                    result_lines = result_lines[:-1]
                    result = '\n'.join(result_lines)
            
            # If patch ends with empty line after hunk header, it might be incomplete
            elif not last_line and second_last.startswith('@@'):
                logger.warning("Patch ends with empty line after hunk header - removing incomplete hunk")
                result_lines = result_lines[:-2]  # Remove empty line and hunk header
                result = '\n'.join(result_lines)
        
        # Ensure result ends with newline (required by some patch tools)
        if result and not result.endswith('\n'):
            result += '\n'
        
        # FINAL VALIDATION: Ensure patch has minimum required structure
        # Must have at least: diff header, file headers, one hunk, and some content
        has_diff_header = any(line.startswith('diff --git') for line in result.split('\n'))
        has_file_headers = any(line.startswith('---') for line in result.split('\n')) and any(line.startswith('+++') for line in result.split('\n'))
        has_hunk = any(line.startswith('@@') for line in result.split('\n'))
        has_content = any(line.startswith((' ', '+', '-')) for line in result.split('\n'))
        
        if not (has_diff_header or (has_file_headers and has_hunk and has_content)):
            logger.error("Patch validation failed: missing required structure (diff header, file headers, hunk, or content)")
            raise PatchApplicationError("Patch is incomplete or malformed: missing required diff structure - AI model generated invalid patch format")
    
    return result
