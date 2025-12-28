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
    def __init__(self, message: str, exit_code: int, stderr: str, stdout: str = None):
        super().__init__(message, exit_code, stderr)
        self.stdout = stdout


class CodeError(CommandError):
    pass


def run_sfdx(
    command: str,
    cwd: Optional[Path] = None,
    timeout: int = 300,
    json_output: bool = True
) -> Tuple[int, str, str]:
    will_have_json = json_output and '--json' not in command
    if will_have_json:
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
            
            # For JSON output, always check JSON status first before relying on exit code
            json_success = False
            # Check if this command should produce JSON (either explicitly requested or auto-added)
            should_parse_json = json_output or '--json' in command
            
            # Always try to parse JSON from stdout if it exists (for scratch org commands especially)
            if stdout:
                try:
                    # Parse JSON from stdout (handling warnings that may appear before JSON)
                    lines = stdout.strip().split('\n')
                    json_str = None
                    for i, line in enumerate(lines):
                        if line.strip().startswith('{'):
                            json_str = '\n'.join(lines[i:])
                            break
                    
                    if json_str:
                        try:
                            data = json.loads(json_str)
                            json_status = data.get('status')
                            has_result = 'result' in data
                            
                            # If JSON shows success (status 0 or has result), ALWAYS treat as success
                            if json_status == 0 or has_result:
                                json_success = True
                                exit_code = 0  # Override exit code - JSON is authoritative
                            elif json_status and json_status != 0:
                                # JSON explicitly shows error - use JSON status
                                exit_code = json_status
                        except json.JSONDecodeError:
                            # JSON parsing failed - proceed with original exit code
                            pass
                except Exception:
                    # If JSON parsing fails, proceed with original exit code
                    pass
            
            # Filter out CLI update warnings (they don't indicate failure)
            has_warning_only = stderr and "Warning: @salesforce/cli update available" in stderr
            if has_warning_only and len(stderr.strip()) < 150:
                # Only warning, no actual error
                stderr_clean = ""
            else:
                stderr_clean = stderr
            
            # Only raise error if exit code is non-zero AND JSON doesn't indicate success
            # For scratch org creation, always trust JSON if it shows success (even if exit code is non-zero)
            if exit_code != 0 and not json_success:
                # Last chance: for scratch org commands, re-check JSON one more time
                if ('org create' in command.lower() or 'scratch' in command.lower()) and stdout:
                    try:
                        lines = stdout.strip().split('\n')
                        json_str = None
                        for i, line in enumerate(lines):
                            if line.strip().startswith('{'):
                                json_str = '\n'.join(lines[i:])
                                break
                        if json_str:
                            data = json.loads(json_str)
                            if data.get('status') == 0 or 'result' in data:
                                # JSON definitively shows success - override everything
                                json_success = True
                                exit_code = 0
                    except:
                        pass
                
                # Only raise error if we still don't have JSON success
                if exit_code != 0 and not json_success:
                    if 'org create' in command.lower() or 'scratch' in command.lower():
                        raise OrgCreationError(
                            f"Org creation failed: {stderr_clean or stderr}",
                            exit_code,
                            stderr_clean or stderr,
                            stdout  # Include stdout so we can check JSON
                        )
                else:
                    raise CodeError(
                        f"Command failed: {stderr_clean or stderr}",
                        exit_code,
                        stderr_clean or stderr
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
    """
    Parse JSON output from Salesforce CLI, handling warnings that may appear before JSON.
    """
    try:
        # Remove CLI update warnings that appear before JSON
        lines = output.strip().split('\n')
        json_lines = []
        in_json = False
        
        for line in lines:
            # Skip warning lines
            if "Warning: @salesforce/cli update available" in line:
                continue
            # Start collecting JSON when we see { or [
            if line.strip().startswith('{') or line.strip().startswith('['):
                in_json = True
            if in_json:
                json_lines.append(line)
        
        json_str = '\n'.join(json_lines) if json_lines else output.strip()
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise SFDXError(f"Failed to parse JSON output: {str(e)}\nOutput: {output[:500]}")


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
            # Convert Path to string explicitly and quote it (handles spaces in path)
            def_file_str = str(definition_file.resolve())
            # Quote the path to handle spaces
            cmd = f'sf org create scratch --alias {alias} --duration-days {duration_days} --definition-file "{def_file_str}" --set-default'
        
        # For scratch org creation, catch the exception and check JSON from stdout
        try:
            exit_code, stdout, stderr = run_sfdx(cmd, timeout=600)
        except OrgCreationError as e:
            # Get stdout from exception (we added it to the exception)
            stdout_from_exception = getattr(e, 'stdout', None)
            if stdout_from_exception:
                try:
                    data = parse_json_output(stdout_from_exception)
                    if 'result' in data or data.get('status') == 0:
                        # JSON shows success - ignore the error
                        return data.get('result', {})
                except:
                    pass
            # If JSON doesn't show success, re-raise
            raise
        
        # Parse JSON and check result (normal path)
        if stdout:
            data = parse_json_output(stdout)
            if 'result' in data:
                return data['result']
            else:
                error_msg = data.get('message', 'Unknown error')
                raise OrgCreationError(f"Failed to create scratch org: {error_msg}", data.get('status', 1), stderr or "", stdout)
        else:
            raise OrgCreationError("Failed to create scratch org: no output received", 1, "", "")
            
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
        # Get username from alias first
        username = get_scratch_org_username(alias)
        if not username:
            # Try using alias as username directly
            username = alias
        
        cmd = f"sf org delete scratch --target-org {username} --no-prompt"
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
