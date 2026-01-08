"""
Tests for configuration management.
"""
import pytest
import os
import json
import tempfile
from pathlib import Path
from sfbench.config import Config, get_config, set_config


def test_config_defaults():
    """Test that config has sensible defaults."""
    config = Config()
    
    assert config.timeout_setup > 0
    assert config.timeout_run > 0
    assert config.timeout_patch > 0
    assert config.max_retries > 0


def test_config_from_env_var():
    """Test that config reads from environment variables."""
    os.environ["SF_BENCH_TIMEOUT_SETUP"] = "1200"
    os.environ["SF_BENCH_TIMEOUT_MULTIPLIER"] = "2.0"
    
    try:
        config = Config()
        assert config.timeout_setup == 2400  # 1200 * 2.0
    finally:
        # Cleanup
        del os.environ["SF_BENCH_TIMEOUT_SETUP"]
        del os.environ["SF_BENCH_TIMEOUT_MULTIPLIER"]


def test_config_from_file():
    """Test that config reads from JSON file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "timeout_setup": 900,
            "timeout_multiplier": 1.5
        }, f)
        config_file = Path(f.name)
    
    try:
        config = Config(config_file=config_file)
        assert config.timeout_setup == int(900 * 1.5)
    finally:
        config_file.unlink()


def test_config_precedence():
    """Test that env vars take precedence over config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "timeout_setup": 600
        }, f)
        config_file = Path(f.name)
    
    os.environ["SF_BENCH_TIMEOUT_SETUP"] = "1200"
    
    try:
        config = Config(config_file=config_file)
        # Env var should take precedence
        assert config.timeout_setup == 1200
    finally:
        config_file.unlink()
        del os.environ["SF_BENCH_TIMEOUT_SETUP"]


def test_global_config():
    """Test global config instance."""
    config1 = get_config()
    config2 = get_config()
    
    # Should return same instance
    assert config1 is config2


def test_set_config():
    """Test setting global config."""
    original_config = get_config()
    new_config = Config()
    
    set_config(new_config)
    
    assert get_config() is new_config
    
    # Restore
    set_config(original_config)


def test_deterministic_mode():
    """Test deterministic mode configuration."""
    os.environ["SF_BENCH_DETERMINISTIC"] = "true"
    os.environ["SF_BENCH_SEED"] = "42"
    
    try:
        config = Config()
        assert config.deterministic_mode is True
        assert config.random_seed == 42
    finally:
        del os.environ["SF_BENCH_DETERMINISTIC"]
        del os.environ["SF_BENCH_SEED"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
