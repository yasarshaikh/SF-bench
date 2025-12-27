from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime


class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    TIMEOUT = "TIMEOUT"
    ERROR = "ERROR"


class TestResult:
    def __init__(
        self,
        task_id: str,
        status: TestStatus,
        duration: float,
        error_message: str = None,
        details: Dict[str, Any] = None,
        execution_log: Optional[List[str]] = None,
        performance_metrics: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.status = status
        self.duration = duration
        self.error_message = error_message
        self.details = details or {}
        self.execution_log = execution_log or []
        self.performance_metrics = performance_metrics or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'task_id': self.task_id,
            'status': self.status.value,
            'duration': round(self.duration, 2),
            'timestamp': self.timestamp
        }
        
        if self.error_message:
            result['error_message'] = self.error_message
        
        if self.details:
            result['details'] = self.details
        
        if self.execution_log:
            result['execution_log'] = self.execution_log
        
        if self.performance_metrics:
            result['performance_metrics'] = self.performance_metrics
        
        return result


def calculate_pass_rate(results: list[TestResult]) -> Dict[str, Any]:
    total = len(results)
    if total == 0:
        return {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'timeout': 0,
            'error': 0,
            'pass_rate': 0.0
        }
    
    passed = sum(1 for r in results if r.status == TestStatus.PASS)
    failed = sum(1 for r in results if r.status == TestStatus.FAIL)
    timeout = sum(1 for r in results if r.status == TestStatus.TIMEOUT)
    error = sum(1 for r in results if r.status == TestStatus.ERROR)
    
    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'timeout': timeout,
        'error': error,
        'pass_rate': round((passed / total) * 100, 2)
    }
