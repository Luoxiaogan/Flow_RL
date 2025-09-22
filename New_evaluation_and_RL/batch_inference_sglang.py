#!/usr/bin/env python3
"""
Batch inference script for sglang server
批量推理脚本，用于向sglang服务器发送请求并获取响应
"""

import json
import asyncio
import aiohttp
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm.asyncio import tqdm
import sys

# Hardcoded parameters
HOST = "localhost"
PORT = 5010
BATCH_SIZE = 20
INPUT_JSONL = "/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/parquet_and_jsonl_data/test_IMO_0922_QZH.jsonl"
OUTPUT_JSONL = "/Users/luogan/Code/workflow_generation/Flow_RL_RIGHT/New_evaluation_and_RL/test_IMO_0922_QZH_with_responses.jsonl"

# Request configuration
API_ENDPOINT = f"http://{HOST}:{PORT}/chat/completions"
REQUEST_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Model configuration (you can modify these)
MODEL_NAME = "gpt-4"  # This is just a placeholder name
TEMPERATURE = 0.7
MAX_TOKENS = 4096


async def make_request(session: aiohttp.ClientSession, messages: List[Dict[str, str]], idx: int) -> Dict[str, Any]:
    """
    Make a single request to sglang server
    向sglang服务器发送单个请求
    """
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": False  # Set to False for batch processing
    }

    for attempt in range(MAX_RETRIES):
        try:
            async with session.post(
                API_ENDPOINT,
                json=payload,
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
    Extract assistant response content from API response
    从API响应中提取assistant回复内容
    """
    try:
        if "choices" in response and len(response["choices"]) > 0:
            message = response["choices"][0].get("message", {})
            if message.get("role") == "assistant":
                return message.get("content", "")
        return None
    except Exception as e:
        print(f"提取响应内容失败: {e}")
        return None


async def main():
    """
    Main processing function
    主处理函数
    """
    print("="*60)
    print("批量推理脚本启动")
    print(f"服务器地址: {HOST}:{PORT}")
    print(f"批量大小: {BATCH_SIZE}")
    print(f"输入文件: {INPUT_JSONL}")
    print(f"输出文件: {OUTPUT_JSONL}")
    print("="*60)
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
            try:
                data = json.loads(line.strip())
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

                # Small delay between batches to avoid overwhelming the server
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
    print("\n完成!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())