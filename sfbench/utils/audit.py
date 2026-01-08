"""
Audit logging system for SF-Bench evaluations.

Provides comprehensive audit trails with cryptographic hashing for result verification.
All critical operations are logged with timestamps, context, and integrity verification.
"""
import hashlib
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EvaluationAudit:
    """
    Comprehensive audit record for an evaluation.
    
    Includes cryptographic hashes for input/output verification and
    complete execution logs for transparency and reproducibility.
    """
    evaluation_id: str
    timestamp: datetime
    model_name: str
    task_id: str
    input_hash: str  # SHA-256 hash of prompt/input
    output_hash: str  # SHA-256 hash of solution/patch
    scratch_org_id: Optional[str] = None
    execution_logs: List[str] = field(default_factory=list)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    final_status: str = "unknown"
    checkpoint_hash: Optional[str] = None  # For integrity verification
    api_calls: List[Dict[str, Any]] = field(default_factory=list)
    sfdx_commands: List[Dict[str, Any]] = field(default_factory=list)
    git_operations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit record to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert datetime to ISO format string
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationAudit':
        """Create audit record from dictionary."""
        # Convert ISO format string back to datetime
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class AuditLogger:
    """
    Centralized audit logging system.
    
    Provides methods to log all critical operations during evaluation,
    including AI provider API calls, Salesforce CLI commands, git operations,
    and validation results.
    """
    
    def __init__(self, evaluation_id: str, audit_dir: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            evaluation_id: Unique identifier for this evaluation
            audit_dir: Directory to store audit logs (default: logs/{evaluation_id}/audit)
        """
        self.evaluation_id = evaluation_id
        if audit_dir is None:
            audit_dir = Path("logs") / evaluation_id / "audit"
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        self.audit_file = self.audit_dir / "audit.json"
        self.audits: List[EvaluationAudit] = []
        
        # Load existing audits if file exists
        if self.audit_file.exists():
            try:
                with open(self.audit_file) as f:
                    data = json.load(f)
                    self.audits = [EvaluationAudit.from_dict(a) for a in data]
            except Exception as e:
                logger.warning(f"Failed to load existing audit file: {e}")
                self.audits = []
    
    def create_audit(
        self,
        model_name: str,
        task_id: str,
        input_data: str,
        output_data: str,
        scratch_org_id: Optional[str] = None
    ) -> EvaluationAudit:
        """
        Create a new audit record for a task evaluation.
        
        Args:
            model_name: Name of the AI model being evaluated
            task_id: Unique identifier for the task
            input_data: Input prompt/task description
            output_data: Generated solution/patch
            scratch_org_id: ID of the scratch org used
        
        Returns:
            EvaluationAudit instance
        """
        audit = EvaluationAudit(
            evaluation_id=self.evaluation_id,
            timestamp=datetime.utcnow(),
            model_name=model_name,
            task_id=task_id,
            input_hash=self._hash_data(input_data),
            output_hash=self._hash_data(output_data),
            scratch_org_id=scratch_org_id
        )
        self.audits.append(audit)
        return audit
    
    def log_api_call(
        self,
        audit: EvaluationAudit,
        provider: str,
        model: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        duration_ms: float
    ) -> None:
        """
        Log an AI provider API call.
        
        Args:
            audit: Audit record to update
            provider: AI provider name
            model: Model identifier
            request_data: Request payload (without sensitive data)
            response_data: Response payload
            duration_ms: Request duration in milliseconds
        """
        # Remove sensitive data from request
        safe_request = self._sanitize_request(request_data)
        
        audit.api_calls.append({
            'timestamp': datetime.utcnow().isoformat(),
            'provider': provider,
            'model': model,
            'request_hash': self._hash_data(json.dumps(safe_request, sort_keys=True)),
            'response_hash': self._hash_data(json.dumps(response_data, sort_keys=True)),
            'duration_ms': duration_ms,
            'status': 'success' if 'error' not in response_data else 'error'
        })
        self._save_audits()
    
    def log_sfdx_command(
        self,
        audit: EvaluationAudit,
        command: str,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration_ms: float
    ) -> None:
        """
        Log a Salesforce CLI command execution.
        
        Args:
            audit: Audit record to update
            command: Command that was executed
            exit_code: Exit code from command
            stdout: Standard output
            stderr: Standard error
            duration_ms: Command duration in milliseconds
        """
        audit.sfdx_commands.append({
            'timestamp': datetime.utcnow().isoformat(),
            'command': command,
            'exit_code': exit_code,
            'stdout_hash': self._hash_data(stdout),
            'stderr_hash': self._hash_data(stderr),
            'duration_ms': duration_ms
        })
        self._save_audits()
    
    def log_git_operation(
        self,
        audit: EvaluationAudit,
        operation: str,
        command: str,
        success: bool,
        duration_ms: float
    ) -> None:
        """
        Log a git operation.
        
        Args:
            audit: Audit record to update
            operation: Type of operation (clone, checkout, apply_patch, etc.)
            command: Git command executed
            success: Whether operation succeeded
            duration_ms: Operation duration in milliseconds
        """
        audit.git_operations.append({
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'command': command,
            'success': success,
            'duration_ms': duration_ms
        })
        self._save_audits()
    
    def log_execution(
        self,
        audit: EvaluationAudit,
        message: str,
        level: str = "INFO"
    ) -> None:
        """
        Log an execution event.
        
        Args:
            audit: Audit record to update
            message: Log message
            level: Log level (INFO, WARNING, ERROR)
        """
        audit.execution_logs.append({
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message
        })
        self._save_audits()
    
    def update_validation_results(
        self,
        audit: EvaluationAudit,
        results: Dict[str, Any]
    ) -> None:
        """
        Update validation results for an audit record.
        
        Args:
            audit: Audit record to update
            results: Validation results dictionary
        """
        audit.validation_results = results
        self._save_audits()
    
    def finalize_audit(
        self,
        audit: EvaluationAudit,
        status: str,
        checkpoint_hash: Optional[str] = None
    ) -> None:
        """
        Finalize an audit record with final status.
        
        Args:
            audit: Audit record to finalize
            status: Final status (passed, failed, error, etc.)
            checkpoint_hash: Optional checkpoint hash for integrity verification
        """
        audit.final_status = status
        audit.checkpoint_hash = checkpoint_hash
        self._save_audits()
    
    def _hash_data(self, data: str) -> str:
        """Generate SHA-256 hash of data."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _sanitize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from request for logging."""
        sanitized = request_data.copy()
        # Remove API keys and tokens
        if 'headers' in sanitized:
            headers = sanitized['headers'].copy()
            for key in list(headers.keys()):
                if 'key' in key.lower() or 'token' in key.lower() or 'authorization' in key.lower():
                    headers[key] = '***REDACTED***'
            sanitized['headers'] = headers
        return sanitized
    
    def _save_audits(self) -> None:
        """Save all audit records to file."""
        try:
            with open(self.audit_file, 'w') as f:
                json.dump([a.to_dict() for a in self.audits], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save audit file: {e}")
    
    def generate_audit_report(self) -> Dict[str, Any]:
        """
        Generate a summary audit report.
        
        Returns:
            Dictionary with audit summary statistics
        """
        if not self.audits:
            return {
                'evaluation_id': self.evaluation_id,
                'total_tasks': 0,
                'status_counts': {},
                'total_api_calls': 0,
                'total_sfdx_commands': 0,
                'total_git_operations': 0
            }
        
        status_counts = {}
        total_api_calls = 0
        total_sfdx_commands = 0
        total_git_operations = 0
        
        for audit in self.audits:
            status_counts[audit.final_status] = status_counts.get(audit.final_status, 0) + 1
            total_api_calls += len(audit.api_calls)
            total_sfdx_commands += len(audit.sfdx_commands)
            total_git_operations += len(audit.git_operations)
        
        return {
            'evaluation_id': self.evaluation_id,
            'total_tasks': len(self.audits),
            'status_counts': status_counts,
            'total_api_calls': total_api_calls,
            'total_sfdx_commands': total_sfdx_commands,
            'total_git_operations': total_git_operations,
            'audit_file': str(self.audit_file)
        }
