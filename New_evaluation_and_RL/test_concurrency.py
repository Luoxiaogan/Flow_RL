#!/usr/bin/env python3
"""
测试并发控制功能
模拟多个并发请求，验证并发限制是否生效
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import List
from datetime import datetime

# 服务器配置
SERVER_URL = "http://localhost:8899"

# 测试workflow（简单版本，快速执行）
TEST_WORKFLOW = '''
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction='Solve the problem.')
        return solution
'''

async def send_request(session: aiohttp.ClientSession, request_id: int, benchmark: str = "gsm8k") -> dict:
    """
    发送单个请求到reward server
    
    Args:
        session: aiohttp会话
        request_id: 请求ID
        benchmark: 使用的benchmark名称
    
    Returns:
        包含结果的字典
    """
    start_time = time.time()
    
    # 构建请求数据
    request_data = {
        "data_source": benchmark,
        "solution_str": TEST_WORKFLOW,
        "ground_truth": "default",
        "extra_info": {
            "test_cases": [request_id % 10],  # 使用不同的test case
            "data_path": f"Processed_dataset/{benchmark}/test.jsonl"
        }
    }
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 请求 {request_id:2d} - 发送中...")
    
    try:
        async with session.post(
            f"{SERVER_URL}/compute_score",
            json=request_data,
            timeout=aiohttp.ClientTimeout(total=700)  # 设置较长超时
        ) as response:
            response_data = await response.json()
            elapsed = time.time() - start_time
            
            if response.status == 200:
                score = response_data.get('score', 0.0)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 请求 {request_id:2d} - ✅ 成功 (耗时: {elapsed:.2f}s, 分数: {score:.3f})")
                return {
                    "id": request_id,
                    "status": "success",
                    "score": score,
                    "time": elapsed
                }
            elif response.status == 503:
                # 服务器繁忙（排队超时）
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 请求 {request_id:2d} - ⏰ 超时 (耗时: {elapsed:.2f}s) - {response_data.get('message', '')}")
                return {
                    "id": request_id,
                    "status": "timeout",
                    "time": elapsed,
                    "message": response_data.get('message', '')
                }
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 请求 {request_id:2d} - ❌ 失败 (状态码: {response.status})")
                return {
                    "id": request_id,
                    "status": "failed",
                    "time": elapsed,
                    "error": response_data.get('error', 'Unknown error')
                }
                
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 请求 {request_id:2d} - ⏱️ 客户端超时 (耗时: {elapsed:.2f}s)")
        return {
            "id": request_id,
            "status": "client_timeout",
            "time": elapsed
        }
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 请求 {request_id:2d} - 💥 异常: {e}")
        return {
            "id": request_id,
            "status": "error",
            "time": elapsed,
            "error": str(e)
        }

async def test_concurrent_requests(num_requests: int = 10):
    """
    测试并发请求
    
    Args:
        num_requests: 并发请求数量
    """
    print(f"\n{'='*60}")
    print(f"开始并发测试 - {num_requests} 个并发请求")
    print(f"服务器: {SERVER_URL}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 首先检查服务器状态
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/status") as response:
                if response.status == 200:
                    status = await response.json()
                    concurrency = status.get('concurrency', {})
                    print(f"服务器状态:")
                    print(f"  最大并发: {concurrency.get('max_concurrent', 'N/A')}")
                    print(f"  当前活跃: {concurrency.get('active_requests', 'N/A')}")
                    print(f"  可用槽位: {concurrency.get('available_slots', 'N/A')}")
                    print(f"  排队请求: {concurrency.get('queued_requests', 'N/A')}")
                    print()
    except Exception as e:
        print(f"⚠️ 无法获取服务器状态: {e}")
        print()
    
    # 创建会话
    async with aiohttp.ClientSession() as session:
        # 创建所有请求任务
        tasks = []
        benchmarks = ["gsm8k", "mbpp"]  # 使用不同的benchmark
        
        for i in range(num_requests):
            benchmark = benchmarks[i % len(benchmarks)]
            task = send_request(session, i + 1, benchmark)
            tasks.append(task)
        
        # 并发执行所有请求
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
    
    # 统计结果
    print(f"\n{'='*60}")
    print(f"测试完成 - 总耗时: {total_time:.2f}秒")
    print(f"{'='*60}")
    
    # 分析结果
    success_count = sum(1 for r in results if r['status'] == 'success')
    timeout_count = sum(1 for r in results if r['status'] in ['timeout', 'client_timeout'])
    failed_count = sum(1 for r in results if r['status'] in ['failed', 'error'])
    
    avg_time = sum(r['time'] for r in results) / len(results) if results else 0
    success_times = [r['time'] for r in results if r['status'] == 'success']
    avg_success_time = sum(success_times) / len(success_times) if success_times else 0
    
    print(f"\n📊 结果统计:")
    print(f"  总请求数: {num_requests}")
    print(f"  成功: {success_count} ({success_count/num_requests*100:.1f}%)")
    print(f"  超时: {timeout_count} ({timeout_count/num_requests*100:.1f}%)")
    print(f"  失败: {failed_count} ({failed_count/num_requests*100:.1f}%)")
    print(f"  平均响应时间: {avg_time:.2f}秒")
    if success_times:
        print(f"  成功请求平均时间: {avg_success_time:.2f}秒")
    
    # 再次检查服务器状态
    print(f"\n📈 最终服务器状态:")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SERVER_URL}/status") as response:
                if response.status == 200:
                    status = await response.json()
                    stats = status.get('statistics', {})
                    print(f"  总处理: {stats.get('total_processed', 'N/A')}")
                    print(f"  总成功: {stats.get('total_succeeded', 'N/A')}")
                    print(f"  总失败: {stats.get('total_failed', 'N/A')}")
                    print(f"  总超时: {stats.get('total_timeout', 'N/A')}")
                    print(f"  成功率: {stats.get('success_rate', 'N/A')}%")
    except Exception as e:
        print(f"  ⚠️ 无法获取状态: {e}")
    
    print(f"\n{'='*60}\n")

async def main():
    """主函数"""
    # 解析参数
    num_requests = 10  # 默认10个并发请求
    
    if len(sys.argv) > 1:
        try:
            num_requests = int(sys.argv[1])
        except ValueError:
            print(f"⚠️ 无效的请求数量: {sys.argv[1]}, 使用默认值 10")
    
    # 执行测试
    await test_concurrent_requests(num_requests)

if __name__ == "__main__":
    print("ScoreFlow Reward Server 并发测试工具")
    print("用法: python test_concurrency.py [请求数量]")
    print("例如: python test_concurrency.py 20")
    
    # 运行测试
    asyncio.run(main())