"""
InternBootcamp Reward Function for VERL V2
适配新的数据格式，将task信息从reward_model移到extra_info
"""
import os
import sys
import re
import json
import asyncio
import logging
import importlib
import traceback
import random
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiohttp
from datetime import datetime
import time

# 添加必要路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "InternBootcamp"))

# DEBUG模式控制
DEBUG = 0  # 改为1启用debug模式
DEBUG_PATH = CURRENT_DIR / "debug_logs"

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Debug日志记录器
debug_data = {
    "start_time": None,
    "end_time": None,
    "total_duration": None,
    "total_tasks": [],
    "workflows": [],
    "llm_calls": [],
    "errors": []
}

def save_debug_data():
    """保存debug数据到文件"""
    if DEBUG == 1:
        DEBUG_PATH.mkdir(exist_ok=True)
        debug_data["end_time"] = datetime.now().isoformat()
        if debug_data["start_time"]:
            start = datetime.fromisoformat(debug_data["start_time"])
            end = datetime.fromisoformat(debug_data["end_time"])
            debug_data["total_duration"] = (end - start).total_seconds()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = DEBUG_PATH / f"debug_{timestamp}.json"
        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Debug data saved to {debug_file}")

def debug_log(category: str, data: Any, start_time: float = None):
    """记录debug信息，包含时间戳和耗时"""
    if DEBUG == 1:
        # 添加时间戳
        data["timestamp"] = datetime.now().isoformat()
        
        # 计算耗时
        if start_time is not None:
            data["duration"] = time.time() - start_time
        
        # 记录到对应类别
        if category == "task":
            debug_data["total_tasks"].append(data)
        elif category == "workflow":
            debug_data["workflows"].append(data)
        elif category == "llm_call":
            debug_data["llm_calls"].append(data)
        elif category == "error":
            debug_data["errors"].append(data)
        elif category == "init":
            debug_data["start_time"] = data["timestamp"]


class InternBootcampRewardCalculator:
    """
    InternBootcamp任务的reward计算器 V2
    """
    
    def __init__(self, config_path: str = None):
        """初始化reward计算器"""
        init_start = time.time()
        
        # 记录初始化开始
        debug_log("init", {"event": "initialization_start"})
        
        # 加载配置
        if config_path is None:
            config_path = CURRENT_DIR / "config.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self.llm_config = self.config['llm_config']['upstream']
            self.reward_config = self.config.get('reward_config', {})
        else:
            # 默认配置
            self.llm_config = {
                'provider': 'openai',
                'model': 'qwen-turbo',
                'api_key': '956c41bd0f31beaf68b871d4987af4bb',
                'base_url': 'https://idealab.alibaba-inc.com/api/openai/v1',
                'temperature': 0.7
            }
            self.reward_config = {}
        
        # 设置超时和并发限制
        self.timeout = self.reward_config.get('timeout', 30)
        self.max_concurrent = self.reward_config.get('max_concurrent', 5)
        
        # bootcamp类缓存
        self._bootcamp_cache = {}
        
        logger.info("InternBootcampRewardCalculator V2 initialized")
        
        # 记录初始化完成
        debug_log("init", {
            "event": "initialization_complete",
            "config_path": str(config_path),
            "llm_config": self.llm_config,
            "reward_config": self.reward_config
        }, init_start)
    
    def extract_workflow_from_response(self, response: str) -> Optional[str]:
        """
        从LLM response中提取workflow代码
        查找<graph>标签内的内容
        """
        extract_start = time.time()
        
        if not response:
            debug_log("workflow", {
                "event": "extract_workflow_failed",
                "reason": "empty_response",
                "response_length": 0
            }, extract_start)
            return None
        
        # 尝试提取<graph>标签内的代码
        graph_pattern = r'<graph>(.*?)</graph>'
        matches = re.findall(graph_pattern, response, re.DOTALL)
        
        if matches:
            workflow_code = matches[0].strip()
            logger.debug(f"Extracted workflow code: {len(workflow_code)} chars")
            debug_log("workflow", {
                "event": "extract_workflow_success",
                "method": "graph_tag",
                "workflow_length": len(workflow_code),
                "response_length": len(response)
            }, extract_start)
            return workflow_code
        
        # 如果没有找到graph标签，尝试查找class Workflow定义
        class_pattern = r'(class\s+(?:InternBootcampWorkflow|Workflow).*?)(?=class\s+\w+|$)'
        matches = re.findall(class_pattern, response, re.DOTALL)
        
        if matches:
            workflow_code = matches[0].strip()
            logger.debug(f"Extracted workflow class: {len(workflow_code)} chars")
            debug_log("workflow", {
                "event": "extract_workflow_success",
                "method": "class_pattern",
                "workflow_length": len(workflow_code),
                "response_length": len(response)
            }, extract_start)
            return workflow_code
        
        logger.warning("No workflow code found in response")
        debug_log("workflow", {
            "event": "extract_workflow_failed",
            "reason": "no_workflow_found",
            "response_preview": response[:500] if len(response) > 500 else response,
            "response_length": len(response)
        }, extract_start)
        return None
    
    def _load_bootcamp_class(self, task_name: str):
        """动态加载对应的bootcamp类"""
        if task_name in self._bootcamp_cache:
            return self._bootcamp_cache[task_name]
        
        try:
            # 导入bootcamp模块
            module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
            module = importlib.import_module(module_path)
            
            # 获取bootcamp类
            class_name = f"{task_name.capitalize()}bootcamp"
            bootcamp_class = getattr(module, class_name)
            
            self._bootcamp_cache[task_name] = bootcamp_class
            logger.info(f"Loaded bootcamp class: {class_name}")
            return bootcamp_class
            
        except Exception as e:
            logger.error(f"Failed to load bootcamp class for {task_name}: {e}")
            return None
    
    async def call_llm_api(self, prompt: str) -> str:
        """调用LLM API，带有指数回避重试机制"""
        api_start = time.time()
        
        url = self.llm_config['base_url'].rstrip('/') + '/chat/completions'
        headers = {
            'Authorization': f"Bearer {self.llm_config['api_key']}",
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.llm_config['model'],
            'messages': [{"role": "user", "content": prompt}],
            'temperature': self.llm_config.get('temperature', 0.7),
            'max_tokens': 1000
        }
        
        # 记录API调用开始
        debug_log("llm_call", {
            "event": "llm_call_start",
            "url": url,
            "model": self.llm_config['model'],
            "prompt_length": len(prompt),
            "prompt_preview": prompt[:500] if len(prompt) > 500 else prompt,
            "temperature": data['temperature'],
            "max_tokens": data['max_tokens']
        })
        
        # 重试配置
        max_retries = 5  # 最大重试次数
        base_delay = 1.0  # 基础延迟（秒）
        max_delay = 60.0  # 最大延迟（秒）
        
        for attempt in range(max_retries + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=data, headers=headers, timeout=120) as response:
                        result = await response.json()
                        
                        # 检查是否是限流错误
                        if not result.get('success', True) and result.get('code') == 'PL-002':
                            # 这是限流错误
                            if attempt < max_retries:
                                # 计算延迟时间：指数回避 + 随机抖动
                                delay = min(base_delay * (2 ** attempt), max_delay)
                                # 添加随机抖动（0.5到1.5倍之间）
                                jitter = random.uniform(0.5, 1.5)
                                actual_delay = delay * jitter
                                
                                logger.warning(f"Rate limit hit (attempt {attempt + 1}/{max_retries + 1}), "
                                             f"retrying in {actual_delay:.2f}s... "
                                             f"Error: {result.get('message', 'Unknown')}")
                                
                                # 记录限流重试
                                debug_log("llm_call", {
                                    "event": "rate_limit_retry",
                                    "attempt": attempt + 1,
                                    "delay": actual_delay,
                                    "error_code": result.get('code'),
                                    "error_message": result.get('message'),
                                    "trace_id": result.get('detailMessage', '').split('traceId: ')[-1] if 'traceId' in result.get('detailMessage', '') else None
                                })
                                
                                await asyncio.sleep(actual_delay)
                                continue
                            else:
                                # 超过最大重试次数
                                logger.error(f"Rate limit persists after {max_retries} retries")
                                debug_log("llm_call", {
                                    "event": "rate_limit_max_retries",
                                    "max_retries": max_retries,
                                    "error": result
                                }, api_start)
                                return ""

                        # 非限流错误，正常处理响应
                        if 'choices' in result and result['choices']:
                            content = result['choices'][0]['message']['content']
                            
                            # 记录API调用成功
                            debug_log("llm_call", {
                                "event": "llm_call_success",
                                "attempt": attempt + 1,
                                "response_length": len(content),
                                "response_preview": content[:500] if len(content) > 500 else content,
                                "usage": result.get('usage', {}),
                                "status_code": response.status
                            }, api_start)
                            
                            return content
                        else:
                            # 其他API错误
                            logger.error(f"Unexpected API response: {result}")
                            debug_log("llm_call", {
                                "event": "llm_call_unexpected_response",
                                "response": result,
                                "status_code": response.status
                            }, api_start)
                            return ""
                            
            except Exception as e:
                # 网络或其他错误
                if attempt < max_retries:
                    # 对于非限流错误也进行重试
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0.5, 1.5)
                    actual_delay = delay * jitter
                    
                    logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries + 1}), "
                                 f"retrying in {actual_delay:.2f}s... Error: {str(e)}")
                    
                    debug_log("llm_call", {
                        "event": "api_call_retry",
                        "attempt": attempt + 1,
                        "delay": actual_delay,
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    })
                    
                    await asyncio.sleep(actual_delay)
                    continue
                else:
                    # 超过最大重试次数
                    error_details = {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "traceback": traceback.format_exc()
                    }
                    
                    logger.error(f"LLM API call failed after {max_retries} retries: {e}")
                    logger.error(f"Error type: {type(e).__name__}")
                    logger.error(f"Full traceback:\n{traceback.format_exc()}")
                    
                    # 记录API调用失败
                    debug_log("llm_call", {
                        "event": "llm_call_failed",
                        "max_retries": max_retries,
                        "error": error_details,
                        "url": url,
                        "model": self.llm_config['model'],
                        "prompt_length": len(prompt)
                    }, api_start)
                    
                    # 同时记录到错误列表
                    debug_log("error", {
                        "function": "call_llm_api",
                        "error": error_details,
                        "context": {
                            "url": url,
                            "model": self.llm_config['model']
                        }
                    })
                    
                    return ""
        
        # 不应该到达这里，但为了安全起见
        return ""
    
    async def execute_workflow_simple(self, workflow_code: str, problem_text: str) -> str:
        """
        简化的workflow执行方法
        直接调用LLM API而不是使用MetaGPT
        """
        exec_start = time.time()
        
        # 从workflow代码中提取指令
        instruction_pattern = r'instruction\s*=\s*["\']([^"\']+)["\']'
        matches = re.findall(instruction_pattern, workflow_code)
        
        if matches:
            instruction = matches[0]
        else:
            instruction = "Solve the problem step by step."
        
        debug_log("workflow", {
            "event": "execute_workflow_start",
            "instruction": instruction,
            "workflow_code_length": len(workflow_code),
            "problem_text_length": len(problem_text),
            "extracted_from_code": bool(matches)
        })
        
        # 构建完整的prompt
        full_prompt = f"{instruction}\n\nProblem: {problem_text}"
        
        debug_log("workflow", {
            "event": "prompt_constructed",
            "full_prompt": full_prompt,
            "prompt_length": len(full_prompt)
        })
        
        # 调用LLM
        llm_start = time.time()
        result = await self.call_llm_api(full_prompt)
        
        debug_log("workflow", {
            "event": "execute_workflow_completed",
            "llm_call_time": time.time() - llm_start,
            "total_execution_time": time.time() - exec_start,
            "result_length": len(result),
            "result_empty": not bool(result)
        })
        
        return result
    
    async def compute_score_for_testcase(self, workflow_code: str, task_name: str, 
                                        test_case: str) -> float:
        """
        在单个test case上计算分数
        """
        testcase_start = time.time()
        
        debug_log("task", {
            "event": "testcase_start",
            "task_name": task_name,
            "test_case": test_case,
            "workflow_code_length": len(workflow_code)
        })
        
        try:
            # 加载bootcamp类
            bootcamp_class = self._load_bootcamp_class(task_name)
            if not bootcamp_class:
                debug_log("task", {
                    "event": "testcase_failed",
                    "reason": "bootcamp_class_not_found",
                    "task_name": task_name
                }, testcase_start)
                return 0.0
            
            # 解析test case
            if isinstance(test_case, str):
                try:
                    # 尝试解析为JSON
                    case_data = json.loads(test_case.replace("'", '"'))
                except:
                    # 尝试使用eval
                    try:
                        case_data = eval(test_case)
                    except:
                        case_data = {'input': test_case}
            else:
                case_data = test_case
            
            debug_log("task", {
                "event": "test_case_parsed",
                "raw_test_case": test_case,
                "parsed_data": case_data
            })
            
            # 使用bootcamp的prompt_func生成问题文本
            if hasattr(bootcamp_class, 'prompt_func'):
                problem_text = bootcamp_class.prompt_func(case_data)
            else:
                problem_text = str(case_data)
            
            logger.debug(f"Problem text: {problem_text[:100]}...")
            
            debug_log("task", {
                "event": "problem_text_generated",
                "problem_text": problem_text,
                "has_prompt_func": hasattr(bootcamp_class, 'prompt_func')
            })
            
            # 执行workflow（简化版）
            exec_start = time.time()
            result = await self.execute_workflow_simple(workflow_code, problem_text)
            
            debug_log("task", {
                "event": "workflow_executed",
                "execution_time": time.time() - exec_start,
                "result_length": len(str(result)),
                "result_preview": str(result)[:500] if len(str(result)) > 500 else str(result)
            })
            
            logger.debug(f"Workflow result: {str(result)[:100]}...")
            
            # 使用bootcamp的verify_score验证结果
            verify_start = time.time()
            score = bootcamp_class.verify_score(
                model_output=str(result),
                identity=case_data,
                format_score=0.1,
                short_penalty=False,
                format_penalty=False
            )
            
            debug_log("task", {
                "event": "score_verified",
                "score": float(score),
                "verification_time": time.time() - verify_start,
                "task_name": task_name
            })
            
            logger.info(f"Task {task_name} test case score: {score}")
            
            debug_log("task", {
                "event": "testcase_completed",
                "task_name": task_name,
                "score": float(score),
                "total_time": time.time() - testcase_start
            })
            
            return float(score)
            
        except Exception as e:
            logger.error(f"Error computing score for {task_name}: {e}")
            logger.debug(traceback.format_exc())
            
            debug_log("error", {
                "function": "compute_score_for_testcase",
                "task_name": task_name,
                "test_case": test_case,
                "error": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                }
            }, testcase_start)
            
            return 0.0
    
    async def compute_reward_async(self, workflow_code: str, task_name: str, 
                                  test_cases: List[str]) -> float:
        """
        异步计算workflow在所有test cases上的平均reward
        使用优化的并行处理策略
        """
        if not test_cases:
            return 0.0
        
        # 记录开始时间
        batch_start = time.time()
        
        debug_log("task", {
            "event": "batch_compute_start",
            "task_name": task_name,
            "num_test_cases": len(test_cases),
            "max_concurrent": self.max_concurrent
        })
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # 创建进度跟踪
        completed_count = 0
        total_count = len(test_cases)
        progress_lock = asyncio.Lock()
        
        async def update_progress():
            nonlocal completed_count
            async with progress_lock:
                completed_count += 1
                if completed_count % max(1, total_count // 10) == 0:  # 每10%报告一次进度
                    logger.info(f"Progress: {completed_count}/{total_count} test cases completed ({completed_count/total_count*100:.1f}%)")
        
        async def limited_compute(test_case, index):
            async with semaphore:
                # 添加重试机制
                max_retries = 2
                retry_delay = 1.0
                
                for attempt in range(max_retries + 1):
                    try:
                        score = await self.compute_score_for_testcase(workflow_code, task_name, test_case)
                        await update_progress()
                        return (index, score, None)
                    except Exception as e:
                        if attempt < max_retries:
                            logger.warning(f"Test case {index} failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {retry_delay}s...")
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # 指数退避
                        else:
                            logger.error(f"Test case {index} failed after {max_retries + 1} attempts")
                            await update_progress()
                            return (index, 0.0, e)
        
        # 使用asyncio.create_task创建更高效的任务
        tasks = [
            asyncio.create_task(limited_compute(test_case, i))
            for i, test_case in enumerate(test_cases)
        ]
        
        # 使用as_completed实现更灵活的结果处理
        results = []
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
        
        # 按原始顺序排序结果
        results.sort(key=lambda x: x[0])
        
        # 处理结果
        valid_scores = []
        failed_count = 0
        for index, score, error in results:
            if error is not None:
                logger.error(f"Task {index} failed with exception: {error}")
                valid_scores.append(0.0)
                failed_count += 1
                debug_log("error", {
                    "function": "compute_score_for_testcase",
                    "test_case_index": index,
                    "error": {
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                        "traceback": traceback.format_exc() if error else None
                    }
                })
            else:
                valid_scores.append(score)
        
        # 计算平均分
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
        success_rate = (len(valid_scores) - failed_count) / len(valid_scores) if valid_scores else 0.0
        
        logger.info(f"Average score for {task_name}: {avg_score:.3f} "
                   f"({len(valid_scores)} test cases, {success_rate*100:.1f}% success rate)")
        
        debug_log("task", {
            "event": "batch_compute_completed",
            "task_name": task_name,
            "scores": valid_scores,
            "average_score": avg_score,
            "num_test_cases": len(test_cases),
            "failed_count": failed_count,
            "success_rate": success_rate,
            "batch_duration": time.time() - batch_start
        })
        
        return avg_score


# 创建全局计算器实例
_global_calculator = None

def get_calculator():
    """获取全局计算器实例"""
    global _global_calculator
    if _global_calculator is None:
        _global_calculator = InternBootcampRewardCalculator()
    return _global_calculator


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
    # 检查是否已经在事件循环中
    try:
        loop = asyncio.get_running_loop()
        # 如果已经在事件循环中，创建任务并等待
        return loop.run_until_complete(_compute_score_async(solution_str, ground_truth, extra_info))
    except RuntimeError:
        # 如果不在事件循环中，使用 asyncio.run
        return asyncio.run(_compute_score_async(solution_str, ground_truth, extra_info))


async def _compute_score_async(solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    异步计算单个solution的reward分数（内部实现）
    """
    compute_start = time.time()
    
    # 记录任务开始
    debug_log("task", {
        "event": "compute_score_start",
        "ground_truth": ground_truth,
        "extra_info": extra_info,
        "solution_length": len(solution_str) if solution_str else 0
    })
    
    try:
        # 获取计算器实例
        calculator = get_calculator()
        
        # 提取workflow代码
        workflow_code = calculator.extract_workflow_from_response(solution_str)
        if not workflow_code:
            logger.error("No workflow code found in solution")
            debug_log("task", {
                "event": "compute_score_failed",
                "reason": "no_workflow_code",
                "solution_preview": solution_str[:500] if solution_str and len(solution_str) > 500 else solution_str
            }, compute_start)
            return 0.0
        
        # 从extra_info提取必要信息
        task_name = extra_info.get('task_name', '')
        test_cases = extra_info.get('test_cases', [])
        
        if not task_name:
            logger.error("No task_name found in extra_info")
            debug_log("task", {
                "event": "compute_score_failed",
                "reason": "no_task_name",
                "extra_info": extra_info
            }, compute_start)
            return 0.0
        
        logger.info(f"Computing reward for task: {task_name} with {len(test_cases)} test cases")
        
        # 记录任务详情
        debug_log("task", {
            "event": "task_details",
            "task_name": task_name,
            "num_test_cases": len(test_cases),
            "test_cases": test_cases,
            "workflow_code_length": len(workflow_code)
        })
        
        # 使用已有的异步并行方法
        reward = await calculator.compute_reward_async(workflow_code, task_name, test_cases)
        
        logger.info(f"Computed average reward: {reward:.3f}")
        
        # 记录最终结果
        debug_log("task", {
            "event": "compute_score_completed",
            "task_name": task_name,
            "average_reward": reward,
            "num_test_cases": len(test_cases)
        }, compute_start)
        
        # 保存debug数据
        save_debug_data()
        
        return reward
        
    except Exception as e:
        logger.error(f"Error computing score: {e}")
        logger.debug(traceback.format_exc())
        
        # 记录错误
        debug_log("error", {
            "function": "compute_score",
            "error": {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            },
            "context": {
                "extra_info": extra_info,
                "solution_length": len(solution_str) if solution_str else 0
            }
        }, compute_start)
        
        # 保存debug数据
        save_debug_data()
        
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
    
    # 使用异步方式运行测试
    async def test():
        score = await _compute_score_async(test_solution, "default", test_extra_info)
        print(f"Test score: {score}")
    
    asyncio.run(test())