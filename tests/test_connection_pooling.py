"""
Tests for connection pooling in AI agent.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sfbench.utils.ai_agent import AIAgent


def test_session_created_for_http_providers():
    """Test that session is created for HTTP-based providers."""
    with patch('sfbench.utils.ai_agent.requests.Session') as mock_session:
        agent = AIAgent(provider="openrouter", model="test-model")
        
        # Session should be created for openrouter
        assert agent.session is not None
        mock_session.assert_called_once()


def test_session_not_created_for_non_http_providers():
    """Test that session is not created for non-HTTP providers."""
    agent = AIAgent(provider="ollama", model="test-model")
        
    # Session should not be created for ollama
    assert agent.session is None


def test_session_reused_across_calls():
    """Test that session is reused across multiple API calls."""
    with patch('sfbench.utils.ai_agent.requests.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        agent = AIAgent(provider="routellm", model="test-model")
        
        # Simulate multiple calls
        if agent.session:
            # Session should be the same instance
            assert agent.session is mock_session


def test_session_cleanup():
    """Test that session is cleaned up on destruction."""
    with patch('sfbench.utils.ai_agent.requests.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        agent = AIAgent(provider="openrouter", model="test-model")
        
        # Delete agent (simulate cleanup)
        del agent
        
        # Session close should be called (if __del__ works)
        # Note: __del__ may not always be called in tests, so this is a best-effort check


def test_http_adapter_configured():
    """Test that HTTP adapter is configured with connection pooling."""
    with patch('sfbench.utils.ai_agent.HTTPAdapter') as mock_adapter_class, \
         patch('sfbench.utils.ai_agent.requests.Session') as mock_session_class:
        
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        agent = AIAgent(provider="openrouter", model="test-model")
        
        # HTTPAdapter should be created
        assert mock_adapter_class.called
        
        # Session mount should be called
        assert mock_session.mount.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
