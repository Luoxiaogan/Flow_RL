"""
Resource manager for model lifecycle management
"""
import asyncio
import logging
import torch
from typing import Optional, Any
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ModelResourceManager:
    """
    Context manager for model resources
    Ensures proper cleanup even on exceptions
    """
    
    def __init__(self, model_interface):
        """
        Initialize resource manager
        
        Args:
            model_interface: Model interface to manage
        """
        self.model_interface = model_interface
        self.initialized = False
        
    async def __aenter__(self):
        """
        Enter context - initialize model
        """
        try:
            await self.model_interface.initialize()
            self.initialized = True
            logger.debug(f"Model {self.model_interface.model_name} entered context")
            return self.model_interface
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            # Ensure cleanup even if initialization fails
            await self._emergency_cleanup()
            raise
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context - cleanup resources
        """
        if exc_type:
            logger.warning(f"Exiting context with exception: {exc_type.__name__}: {exc_val}")
        
        try:
            await self.model_interface.cleanup()
            logger.debug(f"Model {self.model_interface.model_name} cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            # Force cleanup
            await self._emergency_cleanup()
        
        return False  # Don't suppress exceptions
    
    async def _emergency_cleanup(self):
        """
        Emergency cleanup when normal cleanup fails
        """
        try:
            # For local models, force clear CUDA cache
            if hasattr(self.model_interface, 'model') and self.model_interface.model is not None:
                del self.model_interface.model
                self.model_interface.model = None
            
            if hasattr(self.model_interface, 'tokenizer') and self.model_interface.tokenizer is not None:
                del self.model_interface.tokenizer
                self.model_interface.tokenizer = None
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            
            logger.info(f"Emergency cleanup completed for {self.model_interface.model_name}")
            
        except Exception as e:
            logger.error(f"Emergency cleanup failed: {e}")


@asynccontextmanager
async def managed_model(model_interface):
    """
    Convenience function for using model with resource management
    
    Usage:
        async with managed_model(model) as m:
            result = await m.generate(...)
    """
    manager = ModelResourceManager(model_interface)
    async with manager as model:
        yield model


class GlobalResourceTracker:
    """
    Track all active models globally to ensure cleanup
    """
    _instance = None
    _active_models = []
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def register(cls, model_interface):
        """
        Register a model as active
        """
        async with cls._lock:
            cls._active_models.append(model_interface)
            logger.debug(f"Registered model: {model_interface.model_name}")
    
    @classmethod
    async def unregister(cls, model_interface):
        """
        Unregister a model
        """
        async with cls._lock:
            if model_interface in cls._active_models:
                cls._active_models.remove(model_interface)
                logger.debug(f"Unregistered model: {model_interface.model_name}")
    
    @classmethod
    async def cleanup_all(cls):
        """
        Clean up all registered models
        """
        async with cls._lock:
            if cls._active_models:
                logger.info(f"Cleaning up {len(cls._active_models)} active models")
                
                for model in cls._active_models:
                    try:
                        await model.cleanup()
                    except Exception as e:
                        logger.error(f"Failed to cleanup model {model.model_name}: {e}")
                
                cls._active_models.clear()
                
                # Force CUDA cleanup
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize()
    
    @classmethod
    def get_active_count(cls) -> int:
        """
        Get number of active models
        """
        return len(cls._active_models)