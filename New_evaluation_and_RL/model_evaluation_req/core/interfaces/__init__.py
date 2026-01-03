"""
Model interfaces for local and API-based models
"""

from .model_interface import BaseModelInterface
from .local_model_interface import LocalModelInterface
from .api_model_interface import APIModelInterface

__all__ = [
    'BaseModelInterface',
    'LocalModelInterface',
    'APIModelInterface'
]