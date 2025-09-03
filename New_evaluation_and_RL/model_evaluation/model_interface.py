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
    
    def extract_code(self, text: str) -> str:
        """
        Extract workflow code from generated text
        
        Args:
            text: Generated text containing code
            
        Returns:
            Extracted code string with <code> tags
        """
        # Look for code blocks
        code_patterns = [
            r'<code>(.*?)</code>',  # <code>...</code>
            r'```python\n(.*?)```',  # ```python...```
            r'```\n(.*?)```',        # ```...```
        ]
        
        for pattern in code_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                code = match.group(1).strip()
                if 'class Workflow' in code:
                    return f"<code>\n{code}\n</code>"
        
        # If no code block found, try to extract workflow class directly
        if 'class Workflow' in text:
            start = text.find('class Workflow')
            end = len(text)
            
            # Look for common end markers
            for marker in ['</code>', '```', '\n\n\n', 'Note:', 'Example:', '# ', 'if __name__']:
                pos = text.find(marker, start)
                if pos > start:
                    end = min(end, pos)
            
            code = text[start:end].strip()
            
            # Clean up the code
            lines = code.split('\n')
            # Find the last non-empty line that looks like code
            last_code_line = len(lines)
            for i in range(len(lines) - 1, -1, -1):
                line = lines[i].strip()
                if line and not line.startswith('#') and not line.startswith('"""'):
                    last_code_line = i + 1
                    break
            
            code = '\n'.join(lines[:last_code_line])
            return f"<code>\n{code}\n</code>"
        
        # Return empty if no workflow found
        logger.debug(f"[{self.model_name}] 未能从生成的文本中提取 workflow 代码")
        return ""
    
    async def generate_solution(self, test_sample: Dict[str, Any], **kwargs) -> str:
        """
        Generate workflow solution for a test sample
        
        Args:
            test_sample: Test sample containing prompt
            **kwargs: Generation parameters
            
        Returns:
            Extracted workflow code
        """
        # Extract prompt from sample
        prompt = test_sample.get('prompt', '')
        
        # Generate response
        response = await self.generate(prompt, **kwargs)
        
        # Extract code from response
        solution = self.extract_code(response)
        
        return solution