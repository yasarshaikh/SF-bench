"""
Configuration management for SF-Bench.

Supports environment variables, config files, and defaults with proper precedence.
All timeouts and configuration values can be overridden via environment variables.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class Config:
    """Centralized configuration for SF-Bench."""
    
    # Default timeout values (in seconds)
    DEFAULT_TIMEOUT_SETUP = 600
    DEFAULT_TIMEOUT_RUN = 300
    DEFAULT_TIMEOUT_PATCH = 60
    DEFAULT_TIMEOUT_GIT = 300
    DEFAULT_TIMEOUT_API = 120
    
    # Default retry settings
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_INITIAL_DELAY = 2.0
    
    # Default connection pool settings
    DEFAULT_POOL_CONNECTIONS = 10
    DEFAULT_POOL_MAXSIZE = 20
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to JSON config file
        """
        self.config_file = config_file
        self._config_data: Dict[str, Any] = {}
        
        # Load config file if provided
        if config_file and config_file.exists():
            try:
                with open(config_file) as f:
                    self._config_data = json.load(f)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with precedence: env var > config file > default.
        
        Args:
            key: Configuration key
            default: Default value if not found
        
        Returns:
            Configuration value
        """
        # Check environment variable first (highest precedence)
        env_key = f"SF_BENCH_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            # Try to convert to appropriate type
            try:
                if isinstance(default, bool):
                    return env_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(default, int):
                    return int(env_value)
                elif isinstance(default, float):
                    return float(env_value)
                else:
                    return env_value
            except (ValueError, TypeError):
                logger.warning(f"Could not convert {env_key}={env_value} to {type(default).__name__}, using default")
        
        # Check config file
        if key in self._config_data:
            return self._config_data[key]
        
        # Return default
        return default
    
    @property
    def timeout_setup(self) -> int:
        """Timeout for setup phase (scratch org creation, deployment)."""
        multiplier = self.get('timeout_multiplier', 1.0)
        base_timeout = self.get('timeout_setup', self.DEFAULT_TIMEOUT_SETUP)
        return int(base_timeout * multiplier)
    
    @property
    def timeout_run(self) -> int:
        """Timeout for execution phase (test runs, validation)."""
        multiplier = self.get('timeout_multiplier', 1.0)
        base_timeout = self.get('timeout_run', self.DEFAULT_TIMEOUT_RUN)
        return int(base_timeout * multiplier)
    
    @property
    def timeout_patch(self) -> int:
        """Timeout for patch application."""
        multiplier = self.get('timeout_multiplier', 1.0)
        base_timeout = self.get('timeout_patch', self.DEFAULT_TIMEOUT_PATCH)
        return int(base_timeout * multiplier)
    
    @property
    def timeout_git(self) -> int:
        """Timeout for git operations (clone, checkout)."""
        multiplier = self.get('timeout_multiplier', 1.0)
        base_timeout = self.get('timeout_git', self.DEFAULT_TIMEOUT_GIT)
        return int(base_timeout * multiplier)
    
    @property
    def timeout_api(self) -> int:
        """Timeout for API calls (AI provider requests)."""
        multiplier = self.get('timeout_multiplier', 1.0)
        base_timeout = self.get('timeout_api', self.DEFAULT_TIMEOUT_API)
        return int(base_timeout * multiplier)
    
    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts."""
        return self.get('max_retries', self.DEFAULT_MAX_RETRIES)
    
    @property
    def initial_delay(self) -> float:
        """Initial delay for exponential backoff (seconds)."""
        return self.get('initial_delay', self.DEFAULT_INITIAL_DELAY)
    
    @property
    def pool_connections(self) -> int:
        """Number of connection pools for HTTP sessions."""
        return self.get('pool_connections', self.DEFAULT_POOL_CONNECTIONS)
    
    @property
    def pool_maxsize(self) -> int:
        """Maximum size of connection pool."""
        return self.get('pool_maxsize', self.DEFAULT_POOL_MAXSIZE)
    
    @property
    def deterministic_mode(self) -> bool:
        """Whether to run in deterministic mode (temperature=0, fixed seed)."""
        return self.get('deterministic', False)
    
    @property
    def random_seed(self) -> Optional[int]:
        """Random seed for deterministic mode."""
        seed = self.get('seed', None)
        if seed is not None:
            return int(seed)
        return None


# Global config instance (can be overridden)
_global_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        # Try to load from .sfbench_config.json in project root
        config_file = Path(__file__).parent.parent.parent / ".sfbench_config.json"
        _global_config = Config(config_file if config_file.exists() else None)
    return _global_config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _global_config
    _global_config = config
