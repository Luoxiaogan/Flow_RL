"""
SGLang Server Manager - Manages both local SGLang servers and external API endpoints
Supports both local model deployment via SGLang and external API services
"""
import os
import sys
import json
import time
import logging
import subprocess
import requests
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
import psutil
import signal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for model deployment"""
    model_type: str  # "local" or "api"
    model_path: Optional[str] = None  # For local models
    api_url: Optional[str] = None  # For API models
    api_key: Optional[str] = None  # For API authentication
    api_model: Optional[str] = None  # Model name for API
    port: int = 30000  # For local SGLang server
    tensor_parallel: int = 1  # GPU parallelism
    data_parallel: int = 1  # Data parallelism
    max_tokens: int = 4096  # Maximum tokens
    temperature: float = 0.7  # Sampling temperature


class InferenceBackend(ABC):
    """Abstract base class for inference backends"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response for a prompt"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the backend is healthy"""
        pass
    
    @abstractmethod
    def close(self):
        """Close the backend"""
        pass


class SGLangLocalBackend(InferenceBackend):
    """Local SGLang server backend"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.process = None
        self.base_url = f"http://localhost:{config.port}"
        
    def start_server(self) -> bool:
        """Start the SGLang server"""
        try:
            # Check if port is already in use
            if self._is_port_in_use(self.config.port):
                logger.warning(f"Port {self.config.port} is already in use, attempting to use existing server")
                if self.health_check():
                    logger.info("Existing server is healthy, using it")
                    return True
                else:
                    logger.error("Existing server is not healthy, please free the port")
                    return False
            
            # Build command
            cmd = [
                sys.executable, "-m", "sglang.launch_server",
                "--model-path", self.config.model_path,
                "--port", str(self.config.port),
                "--tp", str(self.config.tensor_parallel),
            ]
            
            if self.config.data_parallel > 1:
                cmd.extend(["--dp", str(self.config.data_parallel)])
            
            # Additional optimizations
            cmd.extend([
                "--enable-flashinfer",
                "--disable-radix-cache",
                "--mem-fraction-static", "0.85"
            ])
            
            logger.info(f"Starting SGLang server with command: {' '.join(cmd)}")
            
            # Start the process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Wait for server to be ready
            for i in range(60):  # Wait up to 60 seconds
                time.sleep(1)
                if self.health_check():
                    logger.info(f"SGLang server started successfully on port {self.config.port}")
                    return True
                
                # Check if process has failed
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    logger.error(f"SGLang server failed to start:\n{stderr}")
                    return False
            
            logger.error("SGLang server failed to start within timeout")
            self.stop_server()
            return False
            
        except Exception as e:
            logger.error(f"Failed to start SGLang server: {e}")
            return False
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    
    def stop_server(self):
        """Stop the SGLang server"""
        if self.process:
            try:
                # Try graceful shutdown
                self.process.terminate()
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None
                logger.info("SGLang server stopped")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using SGLang server"""
        import aiohttp
        
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": "default",
            "messages": prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, timeout=60) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"SGLang generation failed: {error_text}")
                        return ""
            except Exception as e:
                logger.error(f"SGLang generation error: {e}")
                return ""
    
    def health_check(self) -> bool:
        """Check if SGLang server is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def close(self):
        """Close the backend"""
        self.stop_server()


class ExternalAPIBackend(InferenceBackend):
    """External API backend (OpenAI-compatible)"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using external API"""
        import aiohttp
        
        # Support both message format and string format
        messages = prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}]
        
        payload = {
            "model": self.config.api_model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.config.api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"API generation failed: {error_text}")
                        return ""
            except Exception as e:
                logger.error(f"API generation error: {e}")
                return ""
    
    def health_check(self) -> bool:
        """Check if API is accessible"""
        try:
            # Try a minimal request to check connectivity
            response = requests.post(
                self.config.api_url,
                headers=self.headers,
                json={
                    "model": self.config.api_model,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                },
                timeout=10
            )
            return response.status_code in [200, 400]  # 400 might be rate limit
        except Exception as e:
            logger.warning(f"API health check failed: {e}")
            return False
    
    def close(self):
        """Close the backend (no-op for API)"""
        pass


class InferenceManager:
    """Manages inference backends"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.backend = None
        
    def initialize(self) -> bool:
        """Initialize the appropriate backend"""
        try:
            if self.config.model_type == "local":
                if not self.config.model_path:
                    raise ValueError("model_path is required for local models")
                
                self.backend = SGLangLocalBackend(self.config)
                return self.backend.start_server()
                
            elif self.config.model_type == "api":
                if not self.config.api_url or not self.config.api_key:
                    raise ValueError("api_url and api_key are required for API models")
                
                self.backend = ExternalAPIBackend(self.config)
                if self.backend.health_check():
                    logger.info(f"Connected to API backend: {self.config.api_model}")
                    return True
                else:
                    logger.error("Failed to connect to API backend")
                    return False
                    
            else:
                raise ValueError(f"Unknown model type: {self.config.model_type}")
                
        except Exception as e:
            logger.error(f"Failed to initialize backend: {e}")
            return False
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response"""
        if not self.backend:
            raise RuntimeError("Backend not initialized")
        return await self.backend.generate(prompt, **kwargs)
    
    def health_check(self) -> bool:
        """Check backend health"""
        if not self.backend:
            return False
        return self.backend.health_check()
    
    def close(self):
        """Close the manager"""
        if self.backend:
            self.backend.close()
            self.backend = None


def load_config_from_file(config_path: str) -> ModelConfig:
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        data = json.load(f)
    return ModelConfig(**data)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    # Example 1: Local SGLang model
    local_config = ModelConfig(
        model_type="local",
        model_path="/path/to/model",
        port=30000,
        tensor_parallel=2
    )
    
    # Example 2: External API
    api_config = ModelConfig(
        model_type="api",
        api_url="https://api.openai.com/v1/chat/completions",
        api_key="your-api-key",
        api_model="gpt-4",
        temperature=0.7
    )
    
    async def test():
        # Test with local model
        manager = InferenceManager(local_config)
        if manager.initialize():
            response = await manager.generate("What is 2+2?")
            print(f"Response: {response}")
            manager.close()
    
    # asyncio.run(test())