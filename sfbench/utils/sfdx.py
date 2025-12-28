import subprocess
import signal
import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


class SFDXError(Exception):
    pass


class TimeoutError(SFDXError):
    pass


class CommandError(SFDXError):
    def __init__(self, message: str, exit_code: int, stderr: str):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


class OrgCreationError(CommandError):
    pass


class CodeError(CommandError):
    pass


def run_sfdx(
    command: str,
    cwd: Optional[Path] = None,
    timeout: int = 300,
    json_output: bool = True
) -> Tuple[int, str, str]:
    if json_output and '--json' not in command:
        command = f"{command} --json"
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(cwd) if cwd else None,
            text=True,
            preexec_fn=None if subprocess.os.name == 'nt' else lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            exit_code = process.returncode
            
            if exit_code != 0:
                if 'org create' in command.lower() or 'scratch' in command.lower():
                    raise OrgCreationError(
                        f"Org creation failed: {stderr}",
                        exit_code,
                        stderr
                    )
                else:
                    raise CodeError(
                        f"Command failed: {stderr}",
                        exit_code,
                        stderr
                    )
            
            return exit_code, stdout, stderr
            
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise TimeoutError(f"Command timed out after {timeout} seconds: {command}")
            
    except Exception as e:
        if isinstance(e, (TimeoutError, CommandError)):
            raise
        raise SFDXError(f"Unexpected error running command: {str(e)}")


def parse_json_output(output: str) -> Dict[str, Any]:
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        raise SFDXError(f"Failed to parse JSON output: {str(e)}")


def verify_devhub() -> bool:
    try:
        exit_code, stdout, stderr = run_sfdx("sf org list", timeout=30)
        data = parse_json_output(stdout)
        
        if 'result' in data:
            for org in data.get('result', {}).get('nonScratchOrgs', []):
                if org.get('isDevHub', False):
                    return True
        
        return False
    except Exception:
        return False


def create_scratch_org(
    alias: str,
    duration_days: int = 1,
    definition_file: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Create a scratch org for evaluation.
    
    Args:
        alias: Alias for the scratch org
        duration_days: Duration in days (default: 1)
        definition_file: Optional scratch org definition file
        
    Returns:
        Dictionary with org details (username, orgId, etc.)
    """
    try:
        # Use default definition if not provided
        if definition_file is None:
            definition_file = Path(__file__).parent.parent.parent / "data" / "templates" / "project-scratch-def.json"
        
        if not definition_file.exists():
            # Fallback: create org without definition file
            cmd = f"sf org create scratch --alias {alias} --duration-days {duration_days} --set-default"
        else:
            cmd = f"sf org create scratch --alias {alias} --duration-days {duration_days} --definition-file {definition_file} --set-default"
        
        exit_code, stdout, stderr = run_sfdx(cmd, timeout=600)
        data = parse_json_output(stdout)
        
        if 'result' in data:
            return data['result']
        else:
            raise OrgCreationError("Failed to create scratch org: no result in response", 1, stdout)
            
    except Exception as e:
        if isinstance(e, (OrgCreationError, TimeoutError)):
            raise
        raise OrgCreationError(f"Failed to create scratch org: {str(e)}", 1, str(e))


def delete_scratch_org(alias: str) -> bool:
    """
    Delete a scratch org.
    
    Args:
        alias: Alias of the scratch org to delete
        
    Returns:
        True if successful
    """
    try:
        cmd = f"sf org delete scratch --alias {alias} --no-prompt"
        exit_code, stdout, stderr = run_sfdx(cmd, timeout=60)
        return True
    except Exception as e:
        # Log but don't fail - org might already be deleted
        print(f"⚠️  Warning: Could not delete scratch org {alias}: {str(e)}")
        return False


def get_scratch_org_username(alias: str) -> Optional[str]:
    """
    Get the username for a scratch org alias.
    
    Args:
        alias: Alias of the scratch org
        
    Returns:
        Username or None if not found
    """
    try:
        exit_code, stdout, stderr = run_sfdx("sf org list", timeout=30)
        data = parse_json_output(stdout)
        
        if 'result' in data:
            for org in data.get('result', {}).get('scratchOrgs', []):
                if org.get('alias') == alias:
                    return org.get('username')
        
        return None
    except Exception:
        return None
