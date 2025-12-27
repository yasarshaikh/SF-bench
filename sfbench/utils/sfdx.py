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
