#!/usr/bin/env python3
"""
Batch inference script for API proxy pool
批量推理脚本，用于向API代理池发送请求并获取响应
"""

import json
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm.asyncio import tqdm
import sys

# Hardcoded parameters - 现在使用API代理池
HOST = "localhost"
PORT = 5059  # API代理池端口
BATCH_SIZE = 20
INPUT_JSONL = "/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/generate_parquet_and_jsonl/proportion_data_0923/test.jsonl"
OUTPUT_JSONL = "/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/generate_parquet_and_jsonl/proportion_data_0923/test_gpt4o_mini.jsonl"

# Request configuration
API_ENDPOINT = f"http://{HOST}:{PORT}"  # 标准OpenAI端点 /chat/completions
REQUEST_TIMEOUT = 300  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Model configuration - 这些会被api_pool_config.yaml中的配置覆盖
MODEL_NAME = "gpt-4o-mini-2024-07-18"  # 会被代理池配置覆盖
TEMPERATURE = 0.2  # 会被代理池配置覆盖 
MAX_TOKENS = 4096  # 会被代理池配置覆盖


async def make_request(session: aiohttp.ClientSession, messages: List[Dict[str, str]], idx: int) -> Dict[str, Any]:
    """
    Make a single request to API proxy pool
    向API代理池发送单个请求
    """
    # 构建标准OpenAI格式的请求
    payload = {
        "model": MODEL_NAME,  # 这会被代理池覆盖
        "messages": messages,
        "temperature": TEMPERATURE,  # 这会被代理池覆盖
        "max_tokens": MAX_TOKENS  # 这会被代理池覆盖
    }

    headers = {
        "Content-Type": "application/json",
        # API key可以是任意值，代理池会替换为真实的
        "Authorization": "Bearer dummy-key-will-be-replaced-by-proxy"
    }

    for attempt in range(MAX_RETRIES):
        try:
            async with session.post(
                API_ENDPOINT,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "index": idx,
                        "success": True,
                        "response": result
                    }
                else:
                    error_text = await response.text()
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    return {
                        "index": idx,
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
        except asyncio.TimeoutError:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            return {
                "index": idx,
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            return {
                "index": idx,
                "success": False,
                "error": str(e)
            }


async def process_batch(session: aiohttp.ClientSession, batch: List[tuple]) -> List[Dict[str, Any]]:
    """
    Process a batch of requests concurrently
    并发处理一批请求
    """
    tasks = []
    for idx, data in batch:
        # Extract messages from prompt field
        messages = data.get("prompt", [])
        if not messages:
            print(f"警告: 第 {idx} 行没有prompt字段或为空")
            continue

        task = make_request(session, messages, idx)
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results


def extract_assistant_content(response: Dict[str, Any]) -> Optional[str]:
    """
    Extract assistant response content from OpenAI API response
    从OpenAI API响应中提取assistant回复内容
    """
    try:
        # 标准OpenAI响应格式
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                return choice["message"]["content"]
        return None
    except Exception as e:
        print(f"提取响应内容失败: {e}")
        return None


async def check_server_health() -> bool:
    """
    Check if API proxy pool is healthy
    检查API代理池是否健康运行
    """
    try:
        async with aiohttp.ClientSession() as session:
            # 尝试访问health端点
            async with session.get(f"http://{HOST}:{PORT}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    print(f"✅ API代理池运行正常")
                    print(f"   状态: {health_data.get('status', 'unknown')}")
                    print(f"   API池大小: {health_data.get('api_pool_size', 'unknown')}")
                    print(f"   总速率限制: {health_data.get('total_rate_limit', 'unknown')}")
                    return True
    except aiohttp.ClientConnectorError as e:
        print(f"❌ 无法连接到API代理池 {HOST}:{PORT}")
        print(f"   错误: {e}")
        print(f"   请确认代理服务器已启动:")
        print(f"   python api_key_proxy_pool.py")
        return False
    except Exception as e:
        print(f"❌ 服务器健康检查失败: {e}")
        return False

    print(f"⚠️ API代理池可能未正确响应")
    return False


async def main():
    """
    Main processing function
    主处理函数
    """
    print("="*60)
    print("批量推理脚本启动 (API代理池版本)")
    print(f"代理池地址: {HOST}:{PORT}")
    print(f"批量大小: {BATCH_SIZE}")
    print(f"输入文件: {INPUT_JSONL}")
    print(f"输出文件: {OUTPUT_JSONL}")
    print("="*60)
    print()

    # 检查服务器健康状态
    print("正在检查API代理池状态...")
    if not await check_server_health():
        print("\n❌ 代理池未运行或无法访问，请先启动代理服务器")
        print("运行命令: python api_key_proxy_pool.py")
        sys.exit(1)
    print()

    # Load input data
    print("正在读取输入文件...")
    input_path = Path(INPUT_JSONL)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {INPUT_JSONL}")
        sys.exit(1)

    data_lines = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()  # 去除首尾空白
            if not line:  # 跳过空行
                continue
            try:
                data = json.loads(line)
                data_lines.append((line_num - 1, data))
            except json.JSONDecodeError as e:
                print(f"警告: 第 {line_num} 行JSON解析失败: {e}")

    total_lines = len(data_lines)
    print(f"成功读取 {total_lines} 条数据")
    print()

    # Process in batches
    print("开始批量处理...")
    all_results = {}

    async with aiohttp.ClientSession() as session:
        # Create batches
        batches = [data_lines[i:i+BATCH_SIZE] for i in range(0, total_lines, BATCH_SIZE)]

        # Process each batch with progress bar
        with tqdm(total=total_lines, desc="处理进度") as pbar:
            for batch_num, batch in enumerate(batches, 1):
                print(f"\n处理批次 {batch_num}/{len(batches)} (包含 {len(batch)} 条数据)...")

                results = await process_batch(session, batch)

                # Store results
                for result in results:
                    if result:
                        idx = result["index"]
                        if result["success"]:
                            all_results[idx] = result["response"]
                        else:
                            print(f"  错误 (第 {idx+1} 行): {result['error']}")
                            all_results[idx] = None

                pbar.update(len(batch))

                # Small delay between batches to avoid overwhelming the proxy
                if batch_num < len(batches):
                    await asyncio.sleep(0.5)

    print("\n批量处理完成")
    print(f"成功: {sum(1 for v in all_results.values() if v is not None)} / {total_lines}")

    # Save results
    print("\n正在保存结果...")
    output_path = Path(OUTPUT_JSONL)
    success_count = 0
    failed_count = 0

    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, original_data in data_lines:
            # Add response field
            if idx in all_results and all_results[idx] is not None:
                assistant_content = extract_assistant_content(all_results[idx])
                if assistant_content:
                    # 构建响应对象
                    original_data["response"] = {
                        "role": "assistant",
                        "content": assistant_content,
                        "model": all_results[idx].get("model", MODEL_NAME),
                        "usage": all_results[idx].get("usage", {}),
                        "timestamp": all_results[idx].get("created", int(time.time()))
                    }
                    success_count += 1
                else:
                    original_data["response"] = {
                        "error": "Failed to extract assistant response"
                    }
                    failed_count += 1
            else:
                original_data["response"] = {
                    "error": "Request failed"
                }
                failed_count += 1

            # Write to output file
            f.write(json.dumps(original_data, ensure_ascii=False) + '\n')

    print(f"结果已保存到: {OUTPUT_JSONL}")
    print(f"成功处理: {success_count} 条")
    print(f"处理失败: {failed_count} 条")
    
    # 获取并显示API池统计信息
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{HOST}:{PORT}/stats", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    stats = await resp.json()
                    print("\n" + "="*60)
                    print("API代理池统计信息:")
                    print(f"总请求数: {stats['global_stats']['total']}")
                    print(f"成功: {stats['global_stats']['success']}")
                    print(f"失败: {stats['global_stats']['failed']}")
                    print("="*60)
    except:
        pass  # 忽略统计信息获取失败
    
    print("\n完成!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())