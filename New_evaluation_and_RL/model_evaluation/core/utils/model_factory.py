"""
Model factory for creating appropriate model interfaces
"""
import logging
from typing import Dict, Any
from pathlib import Path

from ..interfaces.model_interface import BaseModelInterface

logger = logging.getLogger(__name__)

class ModelFactory:
    """
    Factory class to create appropriate model interfaces based on configuration
    """
    
    @staticmethod
    def create_model(model_config: Dict[str, Any]) -> BaseModelInterface:
        """
        Create a model interface based on configuration
        
        Args:
            model_config: Model configuration dictionary
            
        Returns:
            Model interface instance
        """
        # Lazy imports to avoid circular dependency
        from ..interfaces.local_model_interface import LocalModelInterface
        from ..interfaces.api_model_interface import APIModelInterface
        
        model_type = model_config.get('type', 'unknown').lower()
        model_name = model_config.get('name', 'unnamed')
        
        logger.info(f"创建模型接口: {model_name} (类型: {model_type})")
        
        if model_type == 'api':
            return APIModelInterface(model_config)
            
        elif model_type in ['local', 'huggingface', 'hf']:
            # Convert simplified config to LocalModelInterface format
            if 'base_model_path' not in model_config and 'path' in model_config:
                model_config['base_model_path'] = model_config['path']
            
            return LocalModelInterface(model_config)
            
        elif model_type == 'local_with_lora':
            # Explicitly handle LoRA models
            if 'base_model_path' not in model_config and 'path' in model_config:
                model_config['base_model_path'] = model_config['path']
            
            if 'lora_path' not in model_config:
                raise ValueError(f"Model {model_name} type is 'local_with_lora' but no 'lora_path' specified")
            
            return LocalModelInterface(model_config)
            
        elif model_type == 'checkpoint':
            # Checkpoint is essentially a local model
            if 'base_model_path' not in model_config and 'path' in model_config:
                model_config['base_model_path'] = model_config['path']
            
            return LocalModelInterface(model_config)
            
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    @staticmethod
    def validate_config(model_config: Dict[str, Any]) -> bool:
        """
        Validate model configuration
        
        Args:
            model_config: Model configuration to validate
            
        Returns:
            True if valid, raises exception otherwise
        """
        # Check required fields
        if 'name' not in model_config:
            raise ValueError("Model configuration must have 'name' field")
        
        if 'type' not in model_config:
            raise ValueError(f"Model {model_config['name']} must have 'type' field")
        
        model_type = model_config['type'].lower()
        
        # Validate based on type
        if model_type == 'api':
            if 'api_endpoints' not in model_config and 'api_endpoint' not in model_config:
                raise ValueError(f"API model {model_config['name']} must have 'api_endpoints' or 'api_endpoint'")
            
            if 'model' not in model_config:
                raise ValueError(f"API model {model_config['name']} must specify 'model' name")
        
        elif model_type in ['local', 'huggingface', 'hf', 'checkpoint']:
            if 'path' not in model_config and 'base_model_path' not in model_config:
                raise ValueError(f"Local model {model_config['name']} must have 'path' or 'base_model_path'")
            
            # Check if path exists for local models
            if model_type in ['local', 'checkpoint']:
                path = model_config.get('path') or model_config.get('base_model_path')
                if not Path(path).exists():
                    logger.warning(f"Model path does not exist: {path}")
        
        elif model_type == 'local_with_lora':
            if 'path' not in model_config and 'base_model_path' not in model_config:
                raise ValueError(f"LoRA model {model_config['name']} must have 'path' or 'base_model_path'")
            
            if 'lora_path' not in model_config:
                raise ValueError(f"LoRA model {model_config['name']} must have 'lora_path'")
            
            # Check paths
            base_path = model_config.get('path') or model_config.get('base_model_path')
            lora_path = model_config.get('lora_path')
            
            if not Path(base_path).exists():
                logger.warning(f"Base model path does not exist: {base_path}")
            
            if not Path(lora_path).exists():
                logger.warning(f"LoRA adapter path does not exist: {lora_path}")
        
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return True