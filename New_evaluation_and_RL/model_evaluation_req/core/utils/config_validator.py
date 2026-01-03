"""
Configuration validator using JSON Schema
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Try to import jsonschema
try:
    from jsonschema import validate, ValidationError, Draft7Validator
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logger.warning("jsonschema not installed. Install with: pip install jsonschema")

class ConfigValidator:
    """
    Validate configuration against schema
    """
    
    # Configuration schema
    CONFIG_SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["test_data", "reward_server", "evaluation", "models"],
        "properties": {
            "test_data": {
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string"},
                    "max_samples": {
                        "oneOf": [
                            {"type": "integer", "minimum": 1},
                            {"type": "null"}
                        ]
                    }
                }
            },
            "reward_server": {
                "type": "object",
                "required": ["url"],
                "properties": {
                    "url": {
                        "type": "string",
                        "pattern": "^https?://.*"
                    }
                }
            },
            "evaluation": {
                "type": "object",
                "required": ["batch_size", "output_dir"],
                "properties": {
                    "batch_size": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 256
                    },
                    "output_dir": {"type": "string"},
                    "save_intermediate": {"type": "boolean"}
                }
            },
            "models": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name", "type"],
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 1
                        },
                        "type": {
                            "type": "string",
                            "enum": ["api", "local", "huggingface", "hf", "checkpoint", "local_with_lora"]
                        }
                    },
                    "allOf": [
                        {
                            "if": {
                                "properties": {"type": {"const": "api"}}
                            },
                            "then": {
                                "required": ["model"],
                                "properties": {
                                    "api_endpoints": {
                                        "oneOf": [
                                            {"type": "string"},
                                            {
                                                "type": "array",
                                                "items": {"type": "string"},
                                                "minItems": 1
                                            }
                                        ]
                                    },
                                    "api_keys": {
                                        "oneOf": [
                                            {"type": "string"},
                                            {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            }
                                        ]
                                    },
                                    "model": {"type": "string"},
                                    "api_type": {
                                        "type": "string",
                                        "enum": ["openai", "azure", "custom"]
                                    },
                                    "max_retries": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "maximum": 10
                                    },
                                    "timeout": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "maximum": 600
                                    }
                                }
                            }
                        },
                        {
                            "if": {
                                "properties": {"type": {"enum": ["local", "huggingface", "hf", "checkpoint"]}}
                            },
                            "then": {
                                "oneOf": [
                                    {"required": ["path"]},
                                    {"required": ["base_model_path"]}
                                ],
                                "properties": {
                                    "path": {"type": "string"},
                                    "base_model_path": {"type": "string"},
                                    "device_map": {"type": "string"},
                                    "torch_dtype": {
                                        "type": "string",
                                        "enum": ["auto", "float32", "float16", "bfloat16"]
                                    },
                                    "load_in_8bit": {"type": "boolean"},
                                    "load_in_4bit": {"type": "boolean"}
                                }
                            }
                        },
                        {
                            "if": {
                                "properties": {"type": {"const": "local_with_lora"}}
                            },
                            "then": {
                                "required": ["lora_path"],
                                "oneOf": [
                                    {"required": ["path"]},
                                    {"required": ["base_model_path"]}
                                ],
                                "properties": {
                                    "lora_path": {"type": "string"}
                                }
                            }
                        }
                    ]
                }
            }
        }
    }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any], strict: bool = False) -> List[str]:
        """
        Validate configuration against schema
        
        Args:
            config: Configuration dictionary
            strict: If True, raise exception on validation error
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema not available, skipping validation")
            return errors
        
        try:
            # Validate against schema
            validate(instance=config, schema=cls.CONFIG_SCHEMA)
            logger.info("Configuration passed schema validation")
            
        except ValidationError as e:
            error_msg = f"Schema validation error: {e.message}"
            if e.path:
                error_msg += f" at {'.'.join(str(p) for p in e.path)}"
            errors.append(error_msg)
            
            if strict:
                raise ValueError(error_msg)
        
        # Additional custom validation
        custom_errors = cls._custom_validation(config)
        errors.extend(custom_errors)
        
        if errors:
            logger.warning(f"Configuration validation found {len(errors)} error(s)")
            for error in errors:
                logger.warning(f"  - {error}")
        
        return errors
    
    @classmethod
    def _custom_validation(cls, config: Dict[str, Any]) -> List[str]:
        """
        Custom validation beyond schema
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check test data path exists
        test_path = config.get('test_data', {}).get('path')
        if test_path:
            # Handle relative paths
            if not Path(test_path).is_absolute():
                # Don't validate relative paths here
                pass
            elif not Path(test_path).exists():
                errors.append(f"Test data file not found: {test_path}")
        
        # Check for duplicate model names
        models = config.get('models', [])
        model_names = [m.get('name') for m in models if m.get('name')]
        if len(model_names) != len(set(model_names)):
            duplicates = [name for name in model_names if model_names.count(name) > 1]
            errors.append(f"Duplicate model names: {', '.join(set(duplicates))}")
        
        # Validate local model paths
        for model in models:
            model_type = model.get('type', '')
            model_name = model.get('name', 'unnamed')
            
            if model_type in ['local', 'checkpoint', 'local_with_lora']:
                # Check base model path
                base_path = model.get('path') or model.get('base_model_path')
                if base_path and Path(base_path).is_absolute():
                    if not Path(base_path).exists():
                        errors.append(f"Model {model_name}: base path not found: {base_path}")
                
                # Check LoRA path
                if model_type == 'local_with_lora':
                    lora_path = model.get('lora_path')
                    if lora_path and Path(lora_path).is_absolute():
                        if not Path(lora_path).exists():
                            errors.append(f"Model {model_name}: LoRA path not found: {lora_path}")
                
                # Check conflicting quantization settings
                if model.get('load_in_8bit') and model.get('load_in_4bit'):
                    errors.append(f"Model {model_name}: Cannot use both 8-bit and 4-bit quantization")
        
        # Validate API models
        for model in models:
            if model.get('type') == 'api':
                model_name = model.get('name', 'unnamed')
                
                # Check endpoints
                endpoints = model.get('api_endpoints') or model.get('api_endpoint')
                if not endpoints:
                    errors.append(f"Model {model_name}: No API endpoints specified")
                
                # Warn about missing API keys
                api_keys = model.get('api_keys')
                if not api_keys:
                    logger.warning(f"Model {model_name}: No API keys specified")
        
        return errors
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get the configuration schema
        
        Returns:
            JSON Schema dictionary
        """
        return cls.CONFIG_SCHEMA
    
    @classmethod
    def save_schema(cls, path: str):
        """
        Save schema to file for reference
        
        Args:
            path: Path to save schema
        """
        with open(path, 'w') as f:
            json.dump(cls.CONFIG_SCHEMA, f, indent=2)
        logger.info(f"Schema saved to {path}")