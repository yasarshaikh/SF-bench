"""
Tests for retry logic with exponential backoff.
"""
import pytest
import time
from unittest.mock import patch, MagicMock
from sfbench.utils.retry import retry_with_backoff


class TransientError(Exception):
    """Transient error that should be retried."""
    pass


class PermanentError(Exception):
    """Permanent error that should not be retried."""
    pass


def test_retry_succeeds_on_second_attempt():
    """Test that retry succeeds after transient failure."""
    call_count = [0]
    
    @retry_with_backoff(max_retries=3, initial_delay=0.1, retry_on=(TransientError,))
    def flaky_function():
        call_count[0] += 1
        if call_count[0] < 2:
            raise TransientError("Temporary failure")
        return "success"
    
    result = flaky_function()
    assert result == "success"
    assert call_count[0] == 2


def test_retry_fails_after_max_retries():
    """Test that retry fails after max retries."""
    call_count = [0]
    
    @retry_with_backoff(max_retries=3, initial_delay=0.1, retry_on=(TransientError,))
    def always_fails():
        call_count[0] += 1
        raise TransientError("Always fails")
    
    with pytest.raises(TransientError):
        always_fails()
    
    assert call_count[0] == 3


def test_retry_exponential_backoff():
    """Test that retry uses exponential backoff."""
    call_times = []
    
    @retry_with_backoff(max_retries=3, initial_delay=0.1, exponential_base=2.0, retry_on=(TransientError,))
    def flaky_function():
        call_times.append(time.time())
        if len(call_times) < 3:
            raise TransientError("Temporary failure")
        return "success"
    
    start_time = time.time()
    result = flaky_function()
    end_time = time.time()
    
    assert result == "success"
    assert len(call_times) == 3
    
    # Check that delays increase exponentially (with some tolerance)
    if len(call_times) >= 2:
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        # delay2 should be approximately 2x delay1 (exponential base = 2.0)
        assert delay2 >= delay1 * 1.5  # Allow some tolerance


def test_retry_does_not_retry_non_retryable_errors():
    """Test that non-retryable errors are not retried."""
    call_count = [0]
    
    @retry_with_backoff(max_retries=3, initial_delay=0.1, retry_on=(TransientError,))
    def raises_permanent_error():
        call_count[0] += 1
        raise PermanentError("Permanent failure")
    
    with pytest.raises(PermanentError):
        raises_permanent_error()
    
    assert call_count[0] == 1  # Should not retry


def test_retry_respects_max_delay():
    """Test that retry respects max_delay cap."""
    call_times = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.1,
        max_delay=0.2,
        exponential_base=10.0,  # Large base to test max_delay cap
        retry_on=(TransientError,)
    )
    def flaky_function():
        call_times.append(time.time())
        if len(call_times) < 3:
            raise TransientError("Temporary failure")
        return "success"
    
    result = flaky_function()
    
    assert result == "success"
    if len(call_times) >= 2:
        delay = call_times[1] - call_times[0]
        # Delay should be capped at max_delay (0.2s)
        assert delay <= 0.3  # Allow some tolerance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
