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
    
    This function tries multiple patch application methods in sequence, giving models a fair
    chance even if their patches have minor formatting issues. Only fails if ALL strategies fail.
    
    Strategies (in order):
    1. git apply --whitespace=fix --ignore-whitespace (strict)
    2. git apply --whitespace=fix --ignore-whitespace --reject (allows partial)
    3. git apply --3way --whitespace=fix (3-way merge for context mismatches)
    4. patch --batch --fuzz=5 -p1 (fuzzy matching, SWE-bench fallback)
    """
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
    """
    lines = patch_diff.split('\n')
    cleaned_lines = []
    in_diff = False
    
    for line in lines:
        # Remove markdown code fences if present
        if line.strip().startswith('```'):
            continue
        
        # Start collecting when we see diff header
        if line.startswith('diff --git') or line.startswith('---') or line.startswith('+++'):
            in_diff = True
        
        if in_diff:
            # Remove trailing whitespace (but preserve intentional whitespace in context)
            if line.startswith(' ') or line.startswith('-') or line.startswith('+'):
                # For diff lines, preserve the leading character but clean trailing whitespace
                cleaned_line = line.rstrip()
                if cleaned_line:  # Don't add empty lines
                    cleaned_lines.append(cleaned_line)
            else:
                # For non-diff lines (headers, etc.), just strip trailing whitespace
                cleaned_lines.append(line.rstrip())
        else:
            # Before diff starts, keep original (might be instructions)
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)
