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
    try:
        result = subprocess.run(
            ['git', 'apply', '--whitespace=fix'],
            input=patch_diff,
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise GitError(f"Failed to apply patch: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        raise GitError(f"Git apply timed out after {timeout} seconds")
    except Exception as e:
        raise GitError(f"Unexpected error applying patch: {str(e)}")
