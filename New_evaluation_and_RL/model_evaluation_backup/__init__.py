"""
Model evaluation module for batch testing and comparison
Supports both local models and API models

Directory structure:
- configs/: Configuration files (YAML)
- scripts/: Executable scripts and entry points
- core/: Core functionality organized by component type
  - interfaces/: Model interface abstractions
  - evaluators/: Batch and unified evaluation logic
  - utils/: Supporting utilities and helpers
"""

# Import all from core module for backward compatibility
from .core import *

# Explicitly re-export for better IDE support
__all__ = [
    # Interfaces
    'BaseModelInterface',
    'LocalModelInterface',
    'APIModelInterface',
    
    # Evaluators
    'ModelEvaluator',
    'BatchModelEvaluator',
    'UnifiedBatchEvaluator',
    
    # Utils
    'APIConnectionPool',
    'ConfigValidator',
    'ModelFactory',
    'ReportGenerator',
    'ModelResourceManager',
    'GlobalResourceTracker',
    'RewardServerChecker',
    'ScoreCollector'
]