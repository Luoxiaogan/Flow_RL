"""
InternBootcamp Reward Function for VERL V2
完全解耦版本，通过API调用reward server
"""
import os
import sys
import json
import asyncio
import logging
import traceback
import aiohttp
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
from pathlib import Path
import numpy as np

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 服务器配置
REWARD_SERVER_URL = "http://localhost:8900"
HEALTH_CHECK_URL = f"{REWARD_SERVER_URL}/health"
COMPUTE_SCORE_URL = f"{REWARD_SERVER_URL}/compute_score"

# 全局线程池执行器
_thread_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="reward_worker")

def convert_to_json_serializable(obj):
    """
    将对象转换为JSON可序列化的格式
    
    Args:
        obj: 任意对象
        
    Returns:
        JSON可序列化的对象
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return [convert_to_json_serializable(item) for item in obj]
    elif hasattr(obj, 'tolist'):  # 其他可能有tolist方法的对象
        try:
            return obj.tolist()
        except:
            return str(obj)
    else:
        try:
            # 尝试JSON序列化，如果失败则转换为字符串
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)

async def check_server_health() -> bool:
    """检查reward server是否可用"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(HEALTH_CHECK_URL, timeout=10) as response:
                return response.status == 200
    except Exception as e:
        logger.warning(f"Server health check failed: {e}")
        return False

async def call_reward_server_api(solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    调用reward server API计算分数
    
    Args:
        solution_str: LLM生成的包含workflow的response
        ground_truth: ground truth信息
        extra_info: 包含task_name和test_cases等额外信息
    
    Returns:
        float: reward分数 (0.0 到 1.0)
    """
    try:
        # 检查服务器健康状态
        if not await check_server_health():
            logger.error("Reward server is not available")
            return 0.0
        
        # 转换extra_info为JSON可序列化格式
        serializable_extra_info = convert_to_json_serializable(extra_info)
        
        # 准备请求数据
        request_data = {
            "solution_str": solution_str,
            "ground_truth": ground_truth,
            "extra_info": serializable_extra_info
        }
        
        logger.debug(f"Request data prepared: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
        
        # 调用API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                COMPUTE_SCORE_URL,
                json=request_data,
                timeout=300  # 5分钟超时
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    if result.get('success'):
                        score = result.get('score', 0.0)
                        logger.info(f"API call successful, score: {score}")
                        return float(score)
                    else:
                        logger.error(f"API call failed: {result.get('error', 'Unknown error')}")
                        return 0.0
                else:
                    logger.error(f"API call failed with status {response.status}")
                    return 0.0
                    
    except asyncio.TimeoutError:
        logger.error("API call timed out")
        return 0.0
    except Exception as e:
        logger.error(f"API call error: {e}")
        logger.debug(traceback.format_exc())
        return 0.0

def _run_async_in_thread(coro):
    """
    在线程中运行异步协程的辅助函数
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

def compute_score(solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    计算单个solution的reward分数（符合VERL接口规范）
    
    Args:
        solution_str: LLM生成的包含workflow的response
        ground_truth: ground truth信息（对于InternBootcamp通常是"default"）
        extra_info: 包含task_name和test_cases等额外信息
    
    Returns:
        float: reward分数 (0.0 到 1.0)
    """
    try:
        # 检查是否已经在事件循环中
        try:
            loop = asyncio.get_running_loop()
            # 如果已经在事件循环中，使用线程池执行异步调用
            logger.info("compute_score called from within event loop, using thread pool")
            future = _thread_executor.submit(
                _run_async_in_thread,
                call_reward_server_api(solution_str, ground_truth, extra_info)
            )
            return future.result(timeout=300)  # 5分钟超时
        except RuntimeError:
            # 如果不在事件循环中，直接在线程中运行
            logger.info("compute_score called from sync context, using thread pool")
            future = _thread_executor.submit(
                _run_async_in_thread,
                call_reward_server_api(solution_str, ground_truth, extra_info)
            )
            return future.result(timeout=300)  # 5分钟超时
            
    except Exception as e:
        logger.error(f"Error computing score: {e}")
        logger.debug(traceback.format_exc())
        return 0.0

async def compute_score_async(solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    异步版本的compute_score函数，用于在事件循环中调用
    
    Args:
        solution_str: LLM生成的包含workflow的response
        ground_truth: ground truth信息（对于InternBootcamp通常是"default"）
        extra_info: 包含task_name和test_cases等额外信息
    
    Returns:
        float: reward分数 (0.0 到 1.0)
    """
    try:
        return await call_reward_server_api(solution_str, ground_truth, extra_info)
    except Exception as e:
        logger.error(f"Error computing score: {e}")
        logger.debug(traceback.format_exc())
        return 0.0

if __name__ == "__main__":
    # 简单测试
    test_solution = """
<graph>
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem
        self.custom = operator.Custom(self.config, self.problem)
    
    async def run_workflow(self):
        solution = await self.custom(instruction="Solve the problem step by step.")
        return solution
</graph>
"""
    
    test_extra_info = {
        'task_name': 'adidyoumean',
        'test_cases': ["{'input': 'hello'}", "{'input': 'hellno'}", "{'input': 'abacaba'}"]
    }
    
    # 测试同步调用
    print("Testing synchronous compute_score...")
    try:
        score = compute_score(test_solution, "default", test_extra_info)
        print(f"Sync test score: {score}")
    except Exception as e:
        print(f"Sync test failed: {e}")
    
    # 测试异步调用
    print("\nTesting asynchronous compute_score_async...")
    async def test_async():
        try:
            score = await compute_score_async(test_solution, "default", test_extra_info)
            print(f"Async test score: {score}")
        except Exception as e:
            print(f"Async test failed: {e}")
    
    # 运行异步测试
    try:
        asyncio.run(test_async())
    except Exception as e:
        print(f"Async test execution failed: {e}")