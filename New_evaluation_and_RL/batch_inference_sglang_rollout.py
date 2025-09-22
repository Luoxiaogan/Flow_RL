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

# 

# python -m sglang.launch_server       --model-path /nas/ganluo/Flow_RL/rl_out/checkpoints_0921_20250921_031524/global_step_100/actor_hf_official       --host 0.0.0.0       --port 30000       --base-gpu-id 0       --mem-fraction-static 0.85

# Hardcoded parameters
HOST = "localhost"
PORT = 30000
BATCH_SIZE = 20
ROLLOUT = 7  # 每个输入生成的响应数量
INPUT_JSONL = "/nas/ganluo/Flow_RL/New_evaluation_and_RL/parquet_and_jsonl_data/test_IMO_0922_QZH.jsonl"
OUTPUT_JSONL = f"/nas/ganluo/Flow_RL/New_evaluation_and_RL/test_IMO_0922_QZH_with_responses_rollout={ROLLOUT}.jsonl"  # 修改输出文件名以区分

# Request configuration
API_ENDPOINT = f"http://{HOST}:{PORT}/generate"  # 使用SGLang原生端点
REQUEST_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Model configuration (you can modify these)
MODEL_NAME = "gpt-4"  # This is just a placeholder name
TEMPERATURE = 0.7
MAX_TOKENS = 4096


async def make_request(session: aiohttp.ClientSession, messages: List[Dict[str, str]], idx: int, rollout_idx: int = 0) -> Dict[str, Any]:
    """
    Make a single request to sglang server
    向sglang服务器发送单个请求
    """
    # 将messages转换为SGLang原生格式的文本
    text_parts = []
    for msg in messages:
        if msg["role"] == "system":
            text_parts.append(f"<|im_start|>system\n{msg['content']}<|im_end|>")
        elif msg["role"] == "user":
            text_parts.append(f"<|im_start|>user\n{msg['content']}<|im_end|>")
    # 添加assistant标记以开始生成
    text_parts.append("<|im_start|>assistant\n")

    text = "\n".join(text_parts)

    # 使用SGLang原生的generate端点格式
    payload = {
        "text": text,
        "sampling_params": {
            "temperature": TEMPERATURE,
            "max_new_tokens": MAX_TOKENS
        }
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
                        "rollout_idx": rollout_idx,
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
                        "rollout_idx": rollout_idx,
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
        except asyncio.TimeoutError:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            return {
                "index": idx,
                "rollout_idx": rollout_idx,
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            return {
                "index": idx,
                "rollout_idx": rollout_idx,
                "success": False,
                "error": str(e)
            }


async def process_batch(session: aiohttp.ClientSession, batch: List[tuple]) -> List[Dict[str, Any]]:
    """
    Process a batch of requests concurrently with rollout
    并发处理一批请求，每个请求生成多个响应
    """
    tasks = []
    for idx, data in batch:
        # Extract messages from prompt field
        messages = data.get("prompt", [])
        if not messages:
            print(f"警告: 第 {idx} 行没有prompt字段或为空")
            continue

        # 为每个输入创建ROLLOUT个请求
        for rollout_idx in range(ROLLOUT):
            task = make_request(session, messages, idx, rollout_idx)
            tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results


def extract_assistant_content(response: Dict[str, Any]) -> Optional[str]:
    """
    Extract assistant response content from API response
    从API响应中提取assistant回复内容
    """
    try:
        # SGLang generate端点直接返回生成的文本
        if "text" in response:
            # 响应包含完整的生成文本
            generated_text = response["text"]
            # 如果有多个输出，取第一个
            if isinstance(generated_text, list):
                generated_text = generated_text[0] if generated_text else ""

            # 清理输出，移除结束标记
            if "<|im_end|>" in generated_text:
                generated_text = generated_text.split("<|im_end|>")[0]

            # 移除可能的开头和结尾空白
            generated_text = generated_text.strip()

            return generated_text
        return None
    except Exception as e:
        print(f"提取响应内容失败: {e}")
        return None


async def check_server_health() -> bool:
    """
    Check if SGLang server is healthy
    检查SGLang服务器是否健康运行
    """
    try:
        async with aiohttp.ClientSession() as session:
            # 尝试访问模型信息端点
            async with session.get(f"http://{HOST}:{PORT}/get_model_info", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    model_info = await resp.json()
                    print(f"✅ SGLang服务器运行正常")
                    print(f"   模型信息: {model_info.get('model_path', 'unknown')}")
                    return True
            # 如果get_model_info失败，尝试health端点
            async with session.get(f"http://{HOST}:{PORT}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    print("✅ SGLang服务器运行正常")
                    return True
    except aiohttp.ClientConnectorError as e:
        print(f"❌ 无法连接到SGLang服务器 {HOST}:{PORT}")
        print(f"   错误: {e}")
        print(f"   请确认服务器已启动:")
        print(f"   python -m sglang.launch_server --model-path <path> --host 0.0.0.0 --port {PORT}")
        return False
    except Exception as e:
        print(f"❌ 服务器健康检查失败: {e}")
        return False

    print(f"⚠️ SGLang服务器可能未正确响应")
    return False


async def main():
    """
    Main processing function
    主处理函数
    """
    print("="*60)
    print("批量推理脚本启动 (Rollout模式)")
    print(f"服务器地址: {HOST}:{PORT}")
    print(f"批量大小: {BATCH_SIZE}")
    print(f"Rollout数量: {ROLLOUT}")
    print(f"输入文件: {INPUT_JSONL}")
    print(f"输出文件: {OUTPUT_JSONL}")
    print(f"预计输出行数: 输入行数 × {ROLLOUT}")
    print("="*60)
    print()

    # 检查服务器健康状态
    print("正在检查SGLang服务器状态...")
    if not await check_server_health():
        print("\n❌ 服务器未运行或无法访问，请先启动服务器")
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
    print(f"开始批量处理 (每个输入将生成{ROLLOUT}个响应)...")
    all_results = {}  # 结构: {idx: {rollout_idx: response}}

    async with aiohttp.ClientSession() as session:
        # Create batches
        batches = [data_lines[i:i+BATCH_SIZE] for i in range(0, total_lines, BATCH_SIZE)]

        # Process each batch with progress bar (总进度为 total_lines * ROLLOUT)
        total_requests = total_lines * ROLLOUT
        with tqdm(total=total_requests, desc="处理进度") as pbar:
            for batch_num, batch in enumerate(batches, 1):
                print(f"\n处理批次 {batch_num}/{len(batches)} (包含 {len(batch)} 条数据, 共 {len(batch) * ROLLOUT} 个请求)...")

                results = await process_batch(session, batch)

                # Store results - 现在需要考虑rollout_idx
                for result in results:
                    if result:
                        idx = result["index"]
                        rollout_idx = result["rollout_idx"]

                        if idx not in all_results:
                            all_results[idx] = {}

                        if result["success"]:
                            all_results[idx][rollout_idx] = result["response"]
                        else:
                            print(f"  错误 (第 {idx+1} 行, Rollout {rollout_idx}): {result['error']}")
                            all_results[idx][rollout_idx] = None

                pbar.update(len(batch) * ROLLOUT)

                # Small delay between batches to avoid overwhelming the server
                if batch_num < len(batches):
                    await asyncio.sleep(0.5)

    print("\n批量处理完成")
    # 统计成功的请求数
    success_requests = sum(
        1 for idx_results in all_results.values()
        for response in idx_results.values()
        if response is not None
    )
    print(f"成功请求: {success_requests} / {total_requests}")

    # Save results - 每个原始输入会产生ROLLOUT行输出
    print("\n正在保存结果...")
    output_path = Path(OUTPUT_JSONL)
    success_count = 0
    failed_count = 0
    total_output_lines = 0

    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, original_data in data_lines:
            # 为每个rollout创建一行输出
            for rollout_idx in range(ROLLOUT):
                # 创建当前rollout的数据副本
                output_data = original_data.copy()

                # 添加generation_id标识
                output_data["generation_id"] = f"{idx}_{rollout_idx}"
                output_data["rollout_index"] = rollout_idx
                output_data["source_index"] = idx

                # Add response field
                if idx in all_results and rollout_idx in all_results[idx] and all_results[idx][rollout_idx] is not None:
                    assistant_content = extract_assistant_content(all_results[idx][rollout_idx])
                    if assistant_content:
                        output_data["response"] = {
                            "role": "assistant",
                            "content": assistant_content,
                            "model": all_results[idx][rollout_idx].get("model", MODEL_NAME),
                            "usage": all_results[idx][rollout_idx].get("usage", {}),
                            "timestamp": all_results[idx][rollout_idx].get("created", int(time.time()))
                        }
                        success_count += 1
                    else:
                        output_data["response"] = {
                            "error": "Failed to extract assistant response"
                        }
                        failed_count += 1
                else:
                    output_data["response"] = {
                        "error": f"Request failed for rollout {rollout_idx}"
                    }
                    failed_count += 1

                # Write to output file
                f.write(json.dumps(output_data, ensure_ascii=False) + '\n')
                total_output_lines += 1

    print(f"结果已保存到: {OUTPUT_JSONL}")
    print(f"输出文件行数: {total_output_lines} (原始 {total_lines} × Rollout {ROLLOUT})")
    print(f"成功生成: {success_count} 条")
    print(f"生成失败: {failed_count} 条")
    print("\n完成!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())