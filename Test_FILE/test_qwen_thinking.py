#!/usr/bin/env python3
"""
Test script to verify qwen-max-latest with thinking features.
"""

import asyncio
import json
import os
# Disable proxy for testing
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('ALL_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)
from openai import AsyncOpenAI

async def test_thinking_api():
    """Test the qwen-max-latest API with thinking features."""
    
    # Configuration from run_workflow_system_drop.sh
    api_config = {
        "provider": "openai",
        "model": "qwen-max-latest",
        "api_key": "956c41bd0f31beaf68b871d4987af4bb",
        "base_url": "https://idealab.alibaba-inc.com/api/openai/v1",
        "stream": False,
        "stream_options": {"include_usage": True},
        "enable_thinking": True,
        "thinking_budget": 1000
    }
    
    # Test message
    messages = [
        {
            "role": "user",
            "content": "please read the text, and think and show thinking test in <think>...</think>, and the revised text in <revised>...</revised>. text: apple is an animal. your answer: <think>...</think>\n\n<revised>...</revised>"
        }
    ]
    
    print("Testing qwen-max-latest with thinking features...")
    print("="*60)
    
    try:
        client = AsyncOpenAI(
            api_key=api_config["api_key"],
            base_url=api_config["base_url"]
        )
        
        # Build kwargs
        kwargs = {
            "model": api_config["model"],
            "messages": messages,
            "stream": api_config["stream"],
            "stream_options": api_config["stream_options"]
        }
        
        # Add thinking parameters via extra_body
        kwargs["extra_body"] = {
            "enable_thinking": api_config["enable_thinking"],
            "thinking_budget": api_config["thinking_budget"]
        }
        
        print(f"Request parameters:")
        print(json.dumps({k: v for k, v in kwargs.items() if k != "messages"}, indent=2))
        print(f"\nMessages: {messages[0]['content'][:100]}...")
        print("\nSending request...")
        
        completion = await client.chat.completions.create(**kwargs)
        
        print("\n" + "="*60)
        print("Response received!")
        print("="*60)
        print(f"Response content:\n{completion.choices[0].message.content}")
        
        if hasattr(completion, 'usage'):
            print(f"\nUsage: {completion.usage}")
        
        print("\n✅ Test successful!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_thinking_api())