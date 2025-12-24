"""
Unified LLM Calling Interface for New_Flow_RL

Supports multiple providers:
- Alibaba DashScope (Qwen models)
- Local vLLM/SGLang servers
- OpenAI-compatible APIs

Inspired by ToolOrchestra's LLM_CALL.py design pattern.
"""

import os
import json
import time
import random
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

from openai import OpenAI


@dataclass
class LLMResponse:
    """Standardized LLM response structure"""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency: float = 0.0
    raw_response: Any = None
    tool_calls: Optional[List[Dict]] = None

    def __str__(self) -> str:
        return self.content


@dataclass
class LLMConfig:
    """LLM provider configuration"""
    provider: str  # dashscope, local_vllm, local_sglang, openai
    base_url: str
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 60


class LLMClient:
    """
    Unified LLM client supporting multiple providers.

    Usage:
        client = LLMClient.from_config("config/config.yaml")
        response = client.call("What is 2+2?")
        print(response.content)
    """

    def __init__(self, configs: Dict[str, LLMConfig]):
        """
        Initialize with multiple provider configs.

        Args:
            configs: Dict mapping provider name to LLMConfig
        """
        self.configs = configs
        self.clients: Dict[str, OpenAI] = {}
        self._init_clients()

    def _init_clients(self):
        """Initialize OpenAI-compatible clients for each provider"""
        for name, config in self.configs.items():
            self.clients[name] = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
                timeout=config.timeout
            )

    @classmethod
    def from_config(cls, config_path: Union[str, Path]) -> "LLMClient":
        """
        Create LLMClient from config.yaml

        Args:
            config_path: Path to config.yaml

        Returns:
            LLMClient instance
        """
        import yaml

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        providers = config.get('llm_providers', {})
        configs = {}

        for name, provider_config in providers.items():
            # Support environment variable substitution
            api_key = provider_config.get('api_key', 'EMPTY')
            if api_key.startswith('${') and api_key.endswith('}'):
                env_var = api_key[2:-1]
                api_key = os.getenv(env_var, 'EMPTY')

            configs[name] = LLMConfig(
                provider=name,
                base_url=provider_config.get('base_url', ''),
                api_key=api_key,
                model=provider_config.get('default_model', 'qwen-turbo'),
                temperature=provider_config.get('temperature', 0.7),
                max_tokens=provider_config.get('max_tokens', 4096),
                timeout=provider_config.get('timeout', 60)
            )

        return cls(configs)

    @classmethod
    def from_env(cls, provider: str = "dashscope") -> "LLMClient":
        """
        Create LLMClient from environment variables.

        Supports:
            DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL
            LOCAL_VLLM_URL
            LOCAL_SGLANG_URL
        """
        configs = {}

        # DashScope (Alibaba Qwen)
        if os.getenv('DASHSCOPE_API_KEY'):
            configs['dashscope'] = LLMConfig(
                provider='dashscope',
                base_url=os.getenv('DASHSCOPE_BASE_URL',
                                   'https://dashscope.aliyuncs.com/compatible-mode/v1'),
                api_key=os.getenv('DASHSCOPE_API_KEY'),
                model=os.getenv('DASHSCOPE_MODEL', 'qwen-turbo')
            )

        # Local vLLM
        if os.getenv('LOCAL_VLLM_URL'):
            configs['local_vllm'] = LLMConfig(
                provider='local_vllm',
                base_url=os.getenv('LOCAL_VLLM_URL'),
                api_key='EMPTY',
                model=os.getenv('LOCAL_VLLM_MODEL', 'Qwen2.5-7B-Instruct')
            )

        # Local SGLang
        if os.getenv('LOCAL_SGLANG_URL'):
            configs['local_sglang'] = LLMConfig(
                provider='local_sglang',
                base_url=os.getenv('LOCAL_SGLANG_URL'),
                api_key='EMPTY',
                model=os.getenv('LOCAL_SGLANG_MODEL', 'Qwen2.5-7B-Instruct')
            )

        if not configs:
            raise ValueError(
                "No LLM provider configured. Set DASHSCOPE_API_KEY, "
                "LOCAL_VLLM_URL, or LOCAL_SGLANG_URL environment variable."
            )

        return cls(configs)

    def call(
        self,
        messages: Union[str, List[Dict[str, str]]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        return_raw: bool = False,
        retry_count: int = 3,
        retry_delay: float = 5.0,
        **kwargs
    ) -> LLMResponse:
        """
        Call LLM with unified interface.

        Args:
            messages: String prompt or list of message dicts
            provider: Provider name (default: first available)
            model: Model name (optional, uses provider default)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Tool definitions for function calling
            return_raw: Return raw OpenAI response object
            retry_count: Number of retries on failure
            retry_delay: Delay between retries (seconds)

        Returns:
            LLMResponse with content, usage, and metadata
        """
        # Normalize messages
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        # Select provider
        if provider is None:
            provider = list(self.configs.keys())[0]

        if provider not in self.configs:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(self.configs.keys())}")

        config = self.configs[provider]
        client = self.clients[provider]

        # Build request parameters
        request_params = {
            "model": model or config.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else config.temperature,
            "max_tokens": max_tokens or config.max_tokens,
        }

        if tools:
            request_params["tools"] = tools

        request_params.update(kwargs)

        # Call with retry
        last_error = None
        for attempt in range(retry_count):
            try:
                start_time = time.time()
                response = client.chat.completions.create(**request_params)
                latency = time.time() - start_time

                # Build standardized response
                message = response.choices[0].message

                return LLMResponse(
                    content=message.content or "",
                    model=response.model,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    },
                    latency=latency,
                    raw_response=response if return_raw else None,
                    tool_calls=[
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                        for tc in (message.tool_calls or [])
                    ] if message.tool_calls else None
                )

            except Exception as e:
                last_error = e
                print(f"LLM call failed (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)

        raise RuntimeError(f"LLM call failed after {retry_count} attempts: {last_error}")

    async def acall(
        self,
        messages: Union[str, List[Dict[str, str]]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Async version of call().

        For now, wraps synchronous call.
        TODO: Use async OpenAI client for true async.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.call(
                messages=messages,
                provider=provider,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                **kwargs
            )
        )


def get_llm_response(
    messages: Union[str, List[Dict[str, str]]],
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    tools: Optional[List[Dict]] = None,
    config_path: Optional[str] = None,
    provider: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function for quick LLM calls.

    Compatible with ToolOrchestra's get_llm_response interface.

    Args:
        messages: String prompt or message list
        model: Model name
        temperature: Sampling temperature
        max_tokens: Max tokens
        tools: Tool definitions
        config_path: Path to config.yaml (optional)
        provider: Provider name (optional)

    Returns:
        Response content string
    """
    # Create client
    if config_path:
        client = LLMClient.from_config(config_path)
    else:
        client = LLMClient.from_env()

    # Call LLM
    response = client.call(
        messages=messages,
        provider=provider,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        tools=tools,
        **kwargs
    )

    return response.content


# Quick test
if __name__ == "__main__":
    import sys

    # Test with environment variables
    print("Testing LLM call...")

    try:
        client = LLMClient.from_env()
        response = client.call("What is 2+2? Answer in one word.")
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")
        print(f"Latency: {response.latency:.2f}s")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set DASHSCOPE_API_KEY environment variable.")
        sys.exit(1)
