"""
Configuration Manager for New_Flow_RL

Provides centralized configuration loading and management.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field

import yaml


@dataclass
class ServiceConfig:
    """Configuration for a service"""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    timeout: int = 60
    max_concurrent: int = 10


@dataclass
class RewardConfig:
    """Configuration for reward calculation"""
    reward_manager: str = "simple"  # simple | multi_dimension
    outcome_weight: float = 0.6
    efficiency_weight: float = 0.3
    preference_weight: float = 0.1


@dataclass
class TrainingConfig:
    """Configuration for RL training"""
    batch_size: int = 16
    learning_rate: float = 5e-7
    total_epochs: int = 3
    save_freq: int = 10
    test_freq: int = 5


class ConfigManager:
    """
    Centralized configuration management.

    Usage:
        config = ConfigManager("config/config.yaml")
        port = config.get("services.reward_server.port", default=8899)
        reward_config = config.get_reward_config()
    """

    def __init__(self, config_path: Union[str, Path]):
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config.yaml
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._tools: Dict[str, Any] = {}
        self._pricing: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load main config and related files"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f) or {}

        # Expand environment variables
        self._config = self._expand_env_vars(self._config)

        # Load tools.json if exists
        tools_path = self.config_path.parent / "tools.json"
        if tools_path.exists():
            with open(tools_path, 'r', encoding='utf-8') as f:
                self._tools = json.load(f)

        # Load pricing.yaml if exists
        pricing_path = self.config_path.parent / "pricing.yaml"
        if pricing_path.exists():
            with open(pricing_path, 'r', encoding='utf-8') as f:
                self._pricing = yaml.safe_load(f) or {}

    def _expand_env_vars(self, obj: Any) -> Any:
        """Recursively expand ${ENV_VAR} patterns in config values"""
        if isinstance(obj, str):
            if obj.startswith('${') and obj.endswith('}'):
                env_var = obj[2:-1]
                return os.getenv(env_var, obj)
            return obj
        elif isinstance(obj, dict):
            return {k: self._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        return obj

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Dot-separated key path (e.g., "services.reward_server.port")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        parts = key.split('.')
        value = self._config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default

        return value

    def get_service_config(self, service_name: str) -> ServiceConfig:
        """Get configuration for a service"""
        service_config = self.get(f"services.{service_name}", {})
        return ServiceConfig(
            enabled=service_config.get('enabled', True),
            host=service_config.get('host', '0.0.0.0'),
            port=service_config.get('port', 8000),
            timeout=service_config.get('timeout', 60),
            max_concurrent=service_config.get('max_concurrent', 10)
        )

    def get_reward_config(self) -> RewardConfig:
        """Get reward configuration"""
        reward_config = self.get("reward", {})
        dimensions = reward_config.get("dimensions", {})
        return RewardConfig(
            reward_manager=reward_config.get("reward_manager", "simple"),
            outcome_weight=dimensions.get("outcome", {}).get("weight", 0.6),
            efficiency_weight=dimensions.get("efficiency", {}).get("weight", 0.3),
            preference_weight=dimensions.get("preference", {}).get("weight", 0.1)
        )

    def get_training_config(self) -> TrainingConfig:
        """Get training configuration"""
        training = self.get("training", {})
        return TrainingConfig(
            batch_size=training.get("data", {}).get("batch_size", 16),
            learning_rate=training.get("actor", {}).get("learning_rate", 5e-7),
            total_epochs=training.get("trainer", {}).get("total_epochs", 3),
            save_freq=training.get("trainer", {}).get("save_freq", 10),
            test_freq=training.get("trainer", {}).get("test_freq", 5)
        )

    def get_tools(self) -> Dict[str, Any]:
        """Get tools configuration from tools.json"""
        return self._tools

    def get_pricing(self) -> Dict[str, Any]:
        """Get pricing configuration from pricing.yaml"""
        return self._pricing

    def get_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific tool definition by name"""
        tools_list = self._tools.get("tools", [])
        for tool in tools_list:
            if tool.get("name") == tool_name:
                return tool
        return None

    def get_model_pricing(self, model_name: str) -> Dict[str, float]:
        """Get pricing for a specific model"""
        models = self._pricing.get("pricing", {}).get("models", {})
        return models.get(model_name, {
            "input_price": 0.5,
            "output_price": 1.5,
            "avg_latency": 1.0
        })

    @property
    def project_root(self) -> Path:
        """Get project root directory"""
        return self.config_path.parent.parent

    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access: config['key']"""
        return self.get(key)

    def reload(self):
        """Reload configuration from file"""
        self._load_config()


# Global config instance (lazy loaded)
_global_config: Optional[ConfigManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get global config instance.

    Args:
        config_path: Path to config.yaml (only used on first call)

    Returns:
        ConfigManager instance
    """
    global _global_config

    if _global_config is None:
        if config_path is None:
            # Try default paths
            default_paths = [
                Path("config/config.yaml"),
                Path("../config/config.yaml"),
                Path(__file__).parent.parent.parent / "config" / "config.yaml"
            ]
            for path in default_paths:
                if path.exists():
                    config_path = str(path)
                    break

        if config_path is None:
            raise FileNotFoundError("No config.yaml found. Please specify path.")

        _global_config = ConfigManager(config_path)

    return _global_config


def reset_config():
    """Reset global config (useful for testing)"""
    global _global_config
    _global_config = None
