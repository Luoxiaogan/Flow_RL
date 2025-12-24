#!/usr/bin/env python3
"""
Test script for llm_call module.

验证点：能通过 llm_call 调用 Qwen API

Usage:
    # 设置环境变量
    export DASHSCOPE_API_KEY="your-api-key"

    # 运行测试
    python scripts/test_llm_call.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.llm_call import LLMClient, LLMConfig, get_llm_response
from src.core.logger import setup_logger, Timer

# 设置日志
logger = setup_logger("test_llm_call", level="DEBUG")


def test_from_env():
    """测试从环境变量创建客户端"""
    logger.info("=" * 50)
    logger.info("Test 1: 从环境变量创建 LLMClient")
    logger.info("=" * 50)

    try:
        client = LLMClient.from_env()
        logger.info(f"可用 providers: {list(client.configs.keys())}")

        with Timer("LLM call", logger):
            response = client.call("What is 2+2? Answer in one word.")

        logger.info(f"Response: {response.content}")
        logger.info(f"Model: {response.model}")
        logger.info(f"Usage: {response.usage}")
        logger.info(f"Latency: {response.latency:.2f}s")

        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_from_config():
    """测试从配置文件创建客户端"""
    logger.info("=" * 50)
    logger.info("Test 2: 从配置文件创建 LLMClient")
    logger.info("=" * 50)

    config_path = project_root / "config" / "config.yaml"

    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return False

    try:
        client = LLMClient.from_config(config_path)
        logger.info(f"可用 providers: {list(client.configs.keys())}")

        # 尝试调用（如果有可用的 provider）
        if client.configs:
            provider = list(client.configs.keys())[0]
            logger.info(f"使用 provider: {provider}")

            with Timer("LLM call from config", logger):
                response = client.call(
                    "请用一句话解释什么是强化学习。",
                    provider=provider
                )

            logger.info(f"Response: {response.content}")
            logger.info(f"Model: {response.model}")

        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_convenience_function():
    """测试便捷函数 get_llm_response"""
    logger.info("=" * 50)
    logger.info("Test 3: 便捷函数 get_llm_response")
    logger.info("=" * 50)

    try:
        with Timer("get_llm_response", logger):
            response = get_llm_response(
                messages="Hello, how are you?",
                temperature=0.5,
                max_tokens=100
            )

        logger.info(f"Response: {response}")
        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def test_message_formats():
    """测试不同的消息格式"""
    logger.info("=" * 50)
    logger.info("Test 4: 不同消息格式")
    logger.info("=" * 50)

    try:
        client = LLMClient.from_env()

        # 测试字符串格式
        logger.info("Testing string format...")
        response1 = client.call("Say 'hello' in Chinese.")
        logger.info(f"String format response: {response1.content}")

        # 测试消息列表格式
        logger.info("Testing message list format...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"}
        ]
        response2 = client.call(messages)
        logger.info(f"Message list response: {response2.content[:100]}...")

        return True
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False


def main():
    """运行所有测试"""
    logger.info("Starting LLM Call Tests")
    logger.info("=" * 60)

    # 检查环境变量
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.warning("DASHSCOPE_API_KEY not set. Some tests may fail.")
        logger.info("Set it with: export DASHSCOPE_API_KEY='your-key'")
    else:
        logger.info("DASHSCOPE_API_KEY is set")

    results = {}

    # 运行测试
    results["from_env"] = test_from_env()
    results["from_config"] = test_from_config()
    results["convenience_function"] = test_convenience_function()
    results["message_formats"] = test_message_formats()

    # 汇总结果
    logger.info("=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)

    passed = 0
    failed = 0
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    logger.info("-" * 40)
    logger.info(f"Total: {passed} passed, {failed} failed")

    if failed > 0:
        logger.warning("Some tests failed. Please check your configuration.")
        return 1
    else:
        logger.info("All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
