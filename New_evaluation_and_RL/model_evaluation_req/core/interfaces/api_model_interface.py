"""
API model interface for OpenAI-compatible APIs
"""
import os
import json
import time
import random
import logging
from typing import List, Dict, Any, Optional, Union
import requests

from .model_interface import BaseModelInterface
from ..utils.api_connection_pool import APIConnectionPool

logger = logging.getLogger(__name__)

class APIModelInterface(BaseModelInterface):
    """
    Interface for API-based models (OpenAI-compatible)
    """
    
    def __init__(self, model_config: Dict[str, Any]):
        """
        Initialize API model interface
        
        Args:
            model_config: Configuration with:
                - name: Model name for display
                - api_endpoints: List of API endpoints (for load balancing)
                - api_keys: List of API keys (corresponding to endpoints)
                - model: Model name for API (e.g., 'gpt-4', 'claude-3')
                - api_type: API type ('openai', 'azure', 'custom')
                - max_retries: Maximum retry attempts (default: 3)
                - retry_delay: Delay between retries in seconds (default: 1)
                - timeout: Request timeout in seconds (default: 60)
                - generation_params: Default generation parameters
        """
        super().__init__(model_config)
        
        # API configuration
        self.api_endpoints = model_config.get('api_endpoints', [])
        self.api_keys = model_config.get('api_keys', [])
        self.model = model_config.get('model', 'gpt-3.5-turbo')
        self.api_type = model_config.get('api_type', 'openai')
        
        # Retry configuration
        self.max_retries = model_config.get('max_retries', 3)
        self.retry_delay = model_config.get('retry_delay', 1)
        self.timeout = model_config.get('timeout', 60)
        
        # Ensure endpoints and keys are lists
        if isinstance(self.api_endpoints, str):
            self.api_endpoints = [self.api_endpoints]
        if isinstance(self.api_keys, str):
            self.api_keys = [self.api_keys]
        
        # Current endpoint index for round-robin
        self.current_endpoint_idx = 0
        
        # Request statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
    def initialize(self):
        """
        Initialize API connection (test connectivity)
        """
        logger.info(f"[{self.model_name}] 初始化API模型")
        logger.info(f"  模型: {self.model}")
        logger.info(f"  API类型: {self.api_type}")
        logger.info(f"  端点数量: {len(self.api_endpoints)}")

        # Test connectivity to first endpoint
        if self.api_endpoints:
            success = self._test_connectivity()
            if success:
                logger.info(f"✓ [{self.model_name}] API连接成功")
            else:
                logger.warning(f"⚠ [{self.model_name}] API连接测试失败，但仍可继续")
        else:
            raise ValueError(f"[{self.model_name}] 未配置API端点")
    
    def _test_connectivity(self) -> bool:
        """
        Test API connectivity
        """
        try:
            # Simple test with minimal tokens
            test_prompt = "Hello"
            response = self.generate(test_prompt, max_new_tokens=5)
            return bool(response)
        except Exception as e:
            logger.warning(f"[{self.model_name}] 连接测试失败: {e}")
            return False
    
    def _get_next_endpoint(self) -> tuple:
        """
        Get next API endpoint and key (round-robin)
        
        Returns:
            Tuple of (endpoint_url, api_key)
        """
        if not self.api_endpoints:
            raise ValueError("No API endpoints configured")
        
        # Round-robin selection
        endpoint = self.api_endpoints[self.current_endpoint_idx]
        
        # Get corresponding API key if available
        if self.current_endpoint_idx < len(self.api_keys):
            api_key = self.api_keys[self.current_endpoint_idx]
        else:
            api_key = self.api_keys[0] if self.api_keys else ""
        
        # Move to next endpoint
        self.current_endpoint_idx = (self.current_endpoint_idx + 1) % len(self.api_endpoints)
        
        return endpoint, api_key
    
    def generate(self,
                 prompt: Union[str, List[Dict[str, str]]],
                 max_new_tokens: int = 4096,
                 temperature: float = 0.7,
                 top_p: float = 0.9,
                 frequency_penalty: float = 0.0,
                 presence_penalty: float = 0.0,
                 stop: Optional[List[str]] = None,
                 **kwargs) -> str:
        """
        Generate response from API
        
        Args:
            prompt: Input prompt (string or chat messages)
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling
            frequency_penalty: Frequency penalty
            presence_penalty: Presence penalty
            stop: Stop sequences
            **kwargs: Additional API parameters
            
        Returns:
            Generated text
        """
        # Convert prompt to messages format
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
        
        # Prepare request data
        request_data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
        }
        
        if stop:
            request_data["stop"] = stop
        
        # Add any additional parameters
        request_data.update(kwargs)
        
        # Try with retries
        last_error = None
        for attempt in range(self.max_retries):
            try:
                endpoint, api_key = self._get_next_endpoint()
                response = self._make_api_request(endpoint, api_key, request_data)

                # Extract generated text based on API type
                if self.api_type == 'openai':
                    generated = response['choices'][0]['message']['content']
                elif self.api_type == 'azure':
                    generated = response['choices'][0]['message']['content']
                else:
                    # Custom API - assume OpenAI format
                    generated = response.get('choices', [{}])[0].get('message', {}).get('content', '')

                self.successful_requests += 1
                return generated

            except Exception as e:
                last_error = e
                logger.warning(f"[{self.model_name}] API请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
        
        # All retries failed
        self.failed_requests += 1
        raise RuntimeError(f"[{self.model_name}] API请求失败: {last_error}")
    
    def _make_api_request(self, endpoint: str, api_key: str, request_data: dict) -> dict:
        """
        Make API request using connection pool
        
        Args:
            endpoint: API endpoint URL
            api_key: API key
            request_data: Request payload
            
        Returns:
            API response
        """
        self.total_requests += 1
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Determine URL based on API type
        if self.api_type == 'openai':
            # Check if this is a proxy server (common ports: 5019, 5010, 5000-5999)
            # Proxy servers will add /v1 themselves based on their target_url config
            import re
            is_proxy = bool(re.search(r':50\d{2}', endpoint))  # Matches :50XX ports
            
            if is_proxy:
                # For proxy servers, send only the API path without /v1
                # The proxy will add /v1 if needed based on its target_url
                url = f"{endpoint.rstrip('/')}/chat/completions"
            else:
                # For direct API endpoints, check if /v1 already exists
                if endpoint.rstrip('/').endswith('/v1'):
                    url = f"{endpoint.rstrip('/')}/chat/completions"
                else:
                    url = f"{endpoint.rstrip('/')}/v1/chat/completions"
            session_key = 'openai'
        elif self.api_type == 'azure':
            # Azure OpenAI has different URL structure
            url = f"{endpoint}/openai/deployments/{self.model}/chat/completions?api-version=2023-05-15"
            headers['api-key'] = api_key
            del headers['Authorization']
            session_key = 'azure'
        else:
            # Custom API - assume OpenAI-compatible
            # Check if this is a proxy server
            import re
            is_proxy = bool(re.search(r':50\d{2}', endpoint))
            
            if is_proxy:
                # For proxy servers, send only the API path
                url = f"{endpoint.rstrip('/')}/chat/completions"
            else:
                url = f"{endpoint.rstrip('/')}/v1/chat/completions"
            session_key = f'custom_{endpoint.replace("://", "_").replace("/", "_")}'
        
        # Get session from pool
        session = APIConnectionPool.get_session(
            key=session_key,
            timeout=self.timeout
        )

        # Make request using pooled session
        try:
            response = session.post(url, json=request_data, headers=headers, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                error_text = response.text
                raise RuntimeError(f"API error {response.status_code}: {error_text}")
        except requests.Timeout:
            raise RuntimeError(f"API request timeout after {self.timeout} seconds")
    
    def cleanup(self):
        """
        Clean up API resources (mainly for statistics logging)
        """
        logger.info(f"[{self.model_name}] API统计:")
        logger.info(f"  总请求: {self.total_requests}")
        logger.info(f"  成功: {self.successful_requests}")
        logger.info(f"  失败: {self.failed_requests}")
        
        if self.total_requests > 0:
            success_rate = self.successful_requests / self.total_requests * 100
            logger.info(f"  成功率: {success_rate:.1f}%")