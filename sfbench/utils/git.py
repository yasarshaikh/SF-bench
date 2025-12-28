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
    Apply a patch to a repository with improved error handling and whitespace fixing.
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
    
    try:
        # Try with whitespace fix first
        result = subprocess.run(
            ['git', 'apply', '--whitespace=fix', '--ignore-whitespace'],
            input=cleaned_patch,
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            return  # Success
        
        # If that fails, try with more lenient options
        result = subprocess.run(
            ['git', 'apply', '--whitespace=fix', '--ignore-whitespace', '--reject'],
            input=cleaned_patch,
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise GitError(f"Failed to apply patch: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        raise GitError(f"Git apply timed out after {timeout} seconds")
    except GitError:
        raise
    except Exception as e:
        raise GitError(f"Unexpected error applying patch: {str(e)}")


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
