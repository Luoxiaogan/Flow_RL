"""
Unified model interface for both local and API models
"""
import re
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class BaseModelInterface(ABC):
    """
    Abstract base class for all model interfaces
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize model interface
        
        Args:
            model_config: Configuration dictionary for the model
        """
        self.model_config = model_config
        self.model_name = model_config.get('name', 'unnamed')
        self.model_type = model_config.get('type', 'unknown')
        
    @abstractmethod
    async def initialize(self):
        """
        Initialize the model (load weights, connect to API, etc.)
        """
        pass
    
    @abstractmethod
    async def generate(self, 
                       prompt: Union[str, List[Dict[str, str]]],
                       **kwargs) -> str:
        """
        Generate response from the model
        
        Args:
            prompt: Input prompt (string or chat messages)
            **kwargs: Generation parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """
        Clean up resources (clear GPU memory, close connections, etc.)
        """
        pass
    
    
    async def generate_solution(self, test_sample: Dict[str, Any], **kwargs) -> str:
        """
        Generate workflow solution for a test sample
        
        Args:
            test_sample: Test sample containing prompt
            **kwargs: Generation parameters
            
        Returns:
            Complete generated response (reward_server will extract code)
        """
        # Extract prompt from sample
        prompt = test_sample.get('prompt', '')
        
        # Generate response and return complete response_str
        # reward_server will handle code extraction
        response = await self.generate(prompt, **kwargs)
        
        return response