"""
ScoreFlow Reward Function for VERL
适配ScoreFlow系统的reward计算器，支持所有benchmark
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
import string
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import time

# 添加必要路径
CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
# 重要：首先添加PROJECT_ROOT，使得ScoreFlow可以被正确导入
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "metagpt_root"))
# 设置METAGPT_PROJECT_ROOT环境变量（如果没有设置）
if "METAGPT_PROJECT_ROOT" not in os.environ:
    os.environ["METAGPT_PROJECT_ROOT"] = str(PROJECT_ROOT / "Test_FILE")
METAGPT_PROJECT_ROOT = Path(os.environ["METAGPT_PROJECT_ROOT"])
# 添加MetaGPT本地路径
METAGPT_LOCAL = PROJECT_ROOT / "Test_FILE" / "metagpt_local" / "metagpt_local"
if METAGPT_LOCAL.exists():
    sys.path.insert(0, str(METAGPT_LOCAL))

# 设置MetaGPT的工作目录和日志目录到Test_FILE
import os
os.environ["METAGPT_WORKSPACE"] = str(METAGPT_PROJECT_ROOT / "workspace")
os.environ["METAGPT_LOG_DIR"] = str(METAGPT_PROJECT_ROOT / "logs")
os.environ["METAGPT_DATA_PATH"] = str(METAGPT_PROJECT_ROOT / "data")

# 创建必要目录
(METAGPT_PROJECT_ROOT / "workspace").mkdir(parents=True, exist_ok=True)
(METAGPT_PROJECT_ROOT / "logs").mkdir(parents=True, exist_ok=True)
(METAGPT_PROJECT_ROOT / "data").mkdir(parents=True, exist_ok=True)

import asyncio as aio
from typing import List as ListType
from metagpt.provider.llm_provider_registry import create_llm_instance
from metagpt.configs.llm_config import LLMConfig, LLMType

# 导入ScoreFlow组件
from ScoreFlow.scripts.base_handler import BenchmarkHandler

# DEBUG模式控制
DEBUG = 1  # 改为1启用debug模式
DEBUG_PATH = PROJECT_ROOT / "Test_FILE" / "debug_logs"  # 存储在Test_FILE目录下

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


class ScoreFlowRewardCalculator:
    """
    ScoreFlow任务的reward计算器
    复用现有的BenchmarkHandler体系
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
                'api_key': 'YOUR_API_KEY',
                'base_url': 'YOUR_BASE_URL',
                'temperature': 0.7
            }
            self.reward_config = {}
        
        # 设置超时和并发限制
        self.timeout = self.reward_config.get('timeout', 180)
        self.max_concurrent = self.reward_config.get('max_concurrent', 5)
        
        # handler缓存
        self._handler_cache = {}
        
        # 加载benchmark mapping
        self.benchmark_mapping = self._load_benchmark_mapping()
        
        logger.info("ScoreFlowRewardCalculator initialized")
        
        # 记录初始化完成
        debug_log("init", {
            "event": "initialization_complete",
            "config_path": str(config_path),
            "llm_config": self.llm_config,
            "reward_config": self.reward_config
        }, init_start)
    
    def _load_benchmark_mapping(self) -> Dict[str, Dict]:
        """Load benchmark mapping from jsonl file"""
        mapping_file = PROJECT_ROOT / "ScoreFlow" / "benchmark_mapping.jsonl"
        if not mapping_file.exists():
            logger.warning(f"Benchmark mapping file not found: {mapping_file}, using default mapping")
            return {}
        
        mapping = {}
        with open(mapping_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    benchmark = data['benchmark']
                    mapping[benchmark] = data
        
        return mapping
    
    def extract_workflow_from_response(self, response: str) -> Optional[str]:
        """
        从LLM response中提取workflow代码
        查找<graph>标签内的内容或class Workflow定义
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
            logger.debug(f"Extracted workflow code from graph tag: {len(workflow_code)} chars")
            debug_log("workflow", {
                "event": "extract_workflow_success",
                "method": "graph_tag",
                "workflow_length": len(workflow_code),
                "response_length": len(response)
            }, extract_start)
            return workflow_code
        
        # 如果没有找到graph标签，尝试查找class Workflow定义
        class_pattern = r'(class\s+Workflow.*?)(?=class\s+\w+|$)'
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
    
    def _load_benchmark_handler(self, benchmark_name: str, dataset_path: str):
        """动态加载对应的benchmark handler"""
        cache_key = f"{benchmark_name}_{dataset_path}"
        if cache_key in self._handler_cache:
            return self._handler_cache[cache_key]
        
        try:
            provider = self.llm_config.get('provider', 'openai')
            api_type_map = {
                'openai': 'OPENAI', 'azure': 'AZURE', 'gemini': 'GEMINI',
                'claude': 'CLAUDE', 'moonshot': 'MOONSHOT',
                'zhipuai': 'ZHIPUAI', 'qianfan': 'QIANFAN',
            }
            
            # 转换为MetaGPT的LLMConfig
            from metagpt.provider.llm_provider_registry import LLMType
            
            # 获取LLMType枚举
            llm_type_str = api_type_map.get(provider.lower(), 'OPENAI')
            llm_type = getattr(LLMType, llm_type_str)
            
            metagpt_config = LLMConfig(
                api_type=llm_type,
                model=self.llm_config.get('model'),
                api_key=self.llm_config.get('api_key'),
                base_url=self.llm_config.get('base_url')
            )
            
            # 查找benchmark映射信息
            benchmark_info = self.benchmark_mapping.get(benchmark_name)
            if benchmark_info:
                # 使用mapping中的handler class名称和路径
                handler_class_name = benchmark_info['handler_class']
                handler_dir = benchmark_info['handler_dir']
                # 将handler_dir转换为Python模块路径 (e.g., "ScoreFlow/scripts/gsm8k" -> "ScoreFlow.scripts.gsm8k")
                handler_module_path = handler_dir.replace('/', '.') + '.handler'
            else:
                # 回退到默认命名规则
                if benchmark_name.startswith("high_level_math"):
                    handler_module_path = "ScoreFlow.scripts.high_level_math.handler"
                    handler_class_name = "HighLevelMathHandler"
                else:
                    handler_module_path = f"ScoreFlow.scripts.{benchmark_name}.handler"
                    handler_class_name = f"{benchmark_name.capitalize()}Handler"
            
            # 导入handler模块
            handler_module = importlib.import_module(handler_module_path)
            
            # 获取handler类
            handler_class = getattr(handler_module, handler_class_name)
            
            # 实例化handler
            handler = handler_class(dataset_path=dataset_path, config=metagpt_config)
            
            self._handler_cache[cache_key] = handler
            logger.info(f"Loaded handler {handler_class_name} for {benchmark_name}")
            return handler
            
        except Exception as e:
            logger.error(f"Failed to load handler for {benchmark_name}: {e}")
            return None
    
    async def execute_workflow_metagpt(self, workflow_code: str, benchmark_name: str, 
                                       test_case_index: int, dataset_path: str) -> str:
        """
        使用MetaGPT框架执行工作流
        完全复用workflow_executor.py的执行逻辑
        """
        exec_start = time.time()
        
        try:
            # 1. 创建临时工作空间 - 存储在Test_FILE目录下
            workspace_dir = PROJECT_ROOT / "Test_FILE" / "workspace" / benchmark_name
            workspace_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            workflow_id = f"reward_{benchmark_name}_{timestamp}_{random_id}"
            
            # 2. 保存工作流文件（用于调试）
            workflow_file = workspace_dir / f"{workflow_id}.py"
            meta_file = workspace_dir / f"{workflow_id}.meta.json"
            
            # 3. 获取Handler并构建脚本
            handler = self._load_benchmark_handler(benchmark_name, dataset_path)
            if not handler:
                raise ValueError(f"Failed to load handler for {benchmark_name}")
            
            # 使用handler构建可执行脚本
            script_parts = handler.build_executable_script(workflow_code, timeout=self.timeout)
            
            # 拼接完整脚本
            full_script_code = (
                script_parts["python_start"] + "\n" +
                script_parts["workflow_code"] + "\n" +
                script_parts["python_end"]
            )
            
            # 保存完整脚本用于调试
            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write(full_script_code)
            
            # 保存元数据
            meta_data = {
                "id": workflow_id,
                "benchmark": benchmark_name,
                "test_case_index": test_case_index,
                "dataset_path": dataset_path,
                "timestamp": timestamp
            }
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, ensure_ascii=False, indent=2)
            
            debug_log("workflow", {
                "event": "metagpt_execution_start",
                "workflow_id": workflow_id,
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "script_length": len(full_script_code),
                "workspace": str(workspace_dir)
            })
            
            # 4. 准备执行环境
            execution_namespace = {}
            
            # 加载operator模块（使用common operators）
            operator_module = importlib.import_module("ScoreFlow.scripts.common.operator")
            
            # 准备全局命名空间
            exec_globals = {
                'asyncio': aio,
                'create': create_llm_instance,
                'operator': operator_module,
                'Literal': getattr(__import__('typing'), 'Literal'),
                'List': ListType,
            }
            
            # 尝试加载benchmark特定的operator_an（如果存在）
            try:
                # 查找benchmark映射信息
                benchmark_info = self.benchmark_mapping.get(benchmark_name)
                if benchmark_info:
                    handler_dir = benchmark_info['handler_dir']
                    # 将handler_dir转换为Python模块路径
                    an_module_path = handler_dir.replace('/', '.') + '.operator_an'
                else:
                    # 回退到默认命名规则
                    if benchmark_name.startswith("high_level_math"):
                        an_module_path = "ScoreFlow.scripts.high_level_math.operator_an"
                    else:
                        an_module_path = f"ScoreFlow.scripts.{benchmark_name}.operator_an"
                
                operator_an_module = importlib.import_module(an_module_path)
                
                # 注入所有公共成员到执行环境
                for attr_name in dir(operator_an_module):
                    if not attr_name.startswith('_'):
                        exec_globals[attr_name] = getattr(operator_an_module, attr_name)
                
                logger.debug(f"Injected {an_module_path} contents into execution environment")
            except ModuleNotFoundError:
                # 如果没有特定的operator_an，尝试使用common的
                try:
                    common_an_module = importlib.import_module("ScoreFlow.scripts.common.operator_an")
                    for attr_name in dir(common_an_module):
                        if not attr_name.startswith('_'):
                            exec_globals[attr_name] = getattr(common_an_module, attr_name)
                    logger.debug("Using common operator_an module")
                except ModuleNotFoundError:
                    logger.debug("No operator_an module found, proceeding without it")
            
            # 5. 执行脚本获取Workflow类
            exec(full_script_code, exec_globals, execution_namespace)
            
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass:
                raise ValueError(f"No 'Workflow' class found in the executed script for {workflow_id}")
            
            # 6. 准备LLM配置
            provider = self.llm_config.get('provider', 'openai')
            api_type_map = {
                'openai': LLMType.OPENAI, 'azure': LLMType.AZURE, 
                'gemini': LLMType.GEMINI, 'claude': LLMType.CLAUDE,
                'moonshot': LLMType.MOONSHOT, 'zhipuai': LLMType.ZHIPUAI,
                'qianfan': LLMType.QIANFAN,
            }
            api_type = api_type_map.get(provider.lower(), LLMType.OPENAI)
            
            metagpt_config = LLMConfig(
                api_type=api_type,
                model=self.llm_config.get('model'),
                api_key=self.llm_config.get('api_key'),
                base_url=self.llm_config.get('base_url')
            )
            
            # 7. 格式化问题文本
            # 使用handler的get_prompt_text方法获取格式化的问题
            problem_text = handler.get_prompt_text([test_case_index])
            
            logger.debug(f"Problem text for {workflow_id}: {problem_text[:200]}...")
            
            # 8. 实例化并执行工作流
            workflow_instance = WorkflowClass(config=metagpt_config, problem=problem_text)
            
            debug_log("workflow", {
                "event": "workflow_instance_created",
                "workflow_id": workflow_id,
                "class_type": str(type(workflow_instance))
            })
            
            # 9. 根据call_signature执行（处理超时参数）
            if "timeout=" in script_parts["call_signature"]:
                # 新版格式，传入timeout参数
                timeout_match = re.search(r'timeout=(\d+)', script_parts["call_signature"])
                if timeout_match:
                    timeout_value = int(timeout_match.group(1))
                    execution_result = await asyncio.wait_for(
                        workflow_instance(timeout=timeout_value),
                        timeout=timeout_value + 10  # 额外10秒缓冲
                    )
                else:
                    execution_result = await asyncio.wait_for(
                        workflow_instance(timeout=self.timeout),
                        timeout=self.timeout + 10
                    )
            else:
                # 旧版格式，不传timeout
                execution_result = await asyncio.wait_for(
                    workflow_instance(),
                    timeout=self.timeout + 10
                )
            
            debug_log("workflow", {
                "event": "metagpt_execution_completed",
                "workflow_id": workflow_id,
                "result_length": len(str(execution_result)),
                "result_type": str(type(execution_result)),
                "execution_time": time.time() - exec_start
            })
            
            logger.info(f"MetaGPT workflow {workflow_id} executed successfully")
            return str(execution_result)
            
        except asyncio.TimeoutError:
            logger.error(f"MetaGPT workflow execution timed out for {benchmark_name}")
            debug_log("error", {
                "function": "execute_workflow_metagpt",
                "error_type": "TimeoutError",
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "execution_time": time.time() - exec_start
            })
            return "Error: Workflow execution timed out"
            
        except Exception as e:
            error_msg = f"MetaGPT workflow execution failed for {benchmark_name}: {e}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            
            debug_log("error", {
                "function": "execute_workflow_metagpt",
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "error": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                },
                "execution_time": time.time() - exec_start
            })
            
            return f"Error: {str(e)}"
    
    async def compute_score_for_testcase(self, workflow_code: str, benchmark_name: str, 
                                        test_case_index: int, dataset_path: str) -> float:
        """
        在单个test case上计算分数
        使用MetaGPT执行并使用handler的judge方法验证
        """
        testcase_start = time.time()
        
        debug_log("task", {
            "event": "testcase_start",
            "benchmark_name": benchmark_name,
            "test_case_index": test_case_index,
            "dataset_path": dataset_path,
            "workflow_code_length": len(workflow_code),
            "execution_mode": "metagpt"
        })
        
        try:
            # 加载handler
            handler = self._load_benchmark_handler(benchmark_name, dataset_path)
            if not handler:
                debug_log("task", {
                    "event": "testcase_failed",
                    "reason": "handler_not_found",
                    "benchmark_name": benchmark_name
                }, testcase_start)
                return 0.0
            
            # 获取验证数据
            verification_data = handler.get_verification_data(test_case_index)
            
            debug_log("task", {
                "event": "verification_data_loaded",
                "test_case_index": test_case_index,
                "has_answer": "answer" in verification_data or "all_answers" in verification_data
            })
            
            # 使用MetaGPT执行workflow
            exec_start = time.time()
            result = await self.execute_workflow_metagpt(
                workflow_code, benchmark_name, test_case_index, dataset_path
            )
            
            debug_log("task", {
                "event": "workflow_executed_via_metagpt",
                "execution_time": time.time() - exec_start,
                "result_length": len(str(result)),
                "result_preview": str(result)[:500] if len(str(result)) > 500 else str(result)
            })
            
            logger.debug(f"MetaGPT workflow result: {str(result)[:100]}...")
            
            # 使用handler的judge方法验证结果
            verify_start = time.time()
            
            # 检查judge是否是协程函数
            import inspect
            if inspect.iscoroutinefunction(handler.judge):
                is_correct = await handler.judge(result, verification_data)
            else:
                is_correct = handler.judge(result, verification_data)
            
            score = 1.0 if is_correct else 0.0
            
            debug_log("task", {
                "event": "score_verified",
                "score": score,
                "is_correct": is_correct,
                "verification_time": time.time() - verify_start,
                "benchmark_name": benchmark_name,
                "execution_mode": "metagpt"
            })
            
            logger.info(f"Benchmark {benchmark_name} test case {test_case_index} score: {score}")
            
            debug_log("task", {
                "event": "testcase_completed",
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "score": score,
                "total_time": time.time() - testcase_start,
                "execution_mode": "metagpt"
            })
            
            return score
            
        except Exception as e:
            logger.error(f"Error computing score for {benchmark_name} index {test_case_index}: {e}")
            logger.debug(traceback.format_exc())
            
            debug_log("error", {
                "function": "compute_score_for_testcase",
                "benchmark_name": benchmark_name,
                "test_case_index": test_case_index,
                "error": {
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc()
                },
                "execution_mode": "metagpt"
            }, testcase_start)
            
            return 0.0
    
    async def compute_reward_async(self, workflow_code: str, benchmark_name: str, 
                                  test_cases: List[int], dataset_path: str) -> float:
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
            "benchmark_name": benchmark_name,
            "num_test_cases": len(test_cases),
            "test_cases": test_cases,
            "dataset_path": dataset_path,
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
        
        async def limited_compute(test_case_index, index):
            async with semaphore:
                try:
                    score = await self.compute_score_for_testcase(
                        workflow_code, benchmark_name, test_case_index, dataset_path
                    )
                    await update_progress()
                    return (index, score, None)
                except Exception as e:
                    logger.error(f"Test case {test_case_index} failed: {e}")
                    await update_progress()
                    return (index, 0.0, e)
        
        # 使用asyncio.create_task创建更高效的任务
        tasks = [
            asyncio.create_task(limited_compute(test_case_index, i))
            for i, test_case_index in enumerate(test_cases)
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
                    "test_case_index": test_cases[index],
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
        
        logger.info(f"Average score for {benchmark_name}: {avg_score:.3f} "
                   f"({len(valid_scores)} test cases, {success_rate*100:.1f}% success rate)")
        
        debug_log("task", {
            "event": "batch_compute_completed",
            "benchmark_name": benchmark_name,
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
        _global_calculator = ScoreFlowRewardCalculator()
    return _global_calculator


def compute_score(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    计算单个solution的reward分数（符合VERL接口规范）
    
    Args:
        data_source: benchmark名称，如 'gsm8k', 'high_level_math_aime2024'
        solution_str: LLM生成的包含workflow的response
        ground_truth: ground truth信息（通常是"default"）
        extra_info: 包含test_cases, data_path等额外信息
    
    Returns:
        float: reward分数 (0.0 到 1.0)
    """
    if data_source.startswith("workflow_"):
        data_source = data_source.replace("workflow_", "")
    try:
        loop = asyncio.get_running_loop()
        # 如果已经在事件循环中，创建任务并等待
        return loop.run_until_complete(_compute_score_async(data_source, solution_str, ground_truth, extra_info))
    except RuntimeError:
        # 如果不在事件循环中，使用 asyncio.run
        return asyncio.run(_compute_score_async(data_source, solution_str, ground_truth, extra_info))


async def _compute_score_async(data_source: str, solution_str: str, ground_truth: str, extra_info: Dict) -> float:
    """
    异步计算单个solution的reward分数（内部实现）
    """
    compute_start = time.time()
    
    # 记录任务开始
    debug_log("task", {
        "event": "compute_score_start",
        "data_source": data_source,
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
        test_cases = extra_info.get('test_cases', [])
        data_path = extra_info.get('data_path', '')
        
        # 处理numpy array的情况
        if hasattr(test_cases, 'tolist'):
            test_cases = test_cases.tolist()
        
        # 解析benchmark名称（处理类似 'high_level_math_aime2024' 的情况）
        # 直接使用data_source作为benchmark名称，因为benchmark_mapping中已有完整名称
        benchmark_name = data_source
        
        if not data_path:
            logger.error("No data_path found in extra_info")
            debug_log("task", {
                "event": "compute_score_failed",
                "reason": "no_data_path",
                "extra_info": extra_info
            }, compute_start)
            return 0.0
        
        # 构建完整的数据路径
        if not os.path.isabs(data_path):
            data_path = os.path.join(PROJECT_ROOT, data_path)
        
        logger.info(f"Computing reward for benchmark: {benchmark_name} with {len(test_cases)} test cases")
        logger.info(f"Data path: {data_path}")
        
        # 记录任务详情
        debug_log("task", {
            "event": "task_details",
            "data_source": data_source,
            "benchmark_name": benchmark_name,
            "num_test_cases": len(test_cases),
            "test_cases": test_cases,
            "data_path": data_path,
            "workflow_code_length": len(workflow_code)
        })
        
        # 使用已有的异步并行方法
        reward = await calculator.compute_reward_async(
            workflow_code, benchmark_name, test_cases, data_path
        )
        
        logger.info(f"Computed average reward: {reward:.3f}")
        
        # 记录最终结果
        debug_log("task", {
            "event": "compute_score_completed",
            "data_source": data_source,
            "benchmark_name": benchmark_name,
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
                "data_source": data_source,
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
        solution = await self.custom(instruction="Solve the math problem step by step.")
        return solution
</graph>
"""
    
    test_extra_info = {
        'data_path': 'Processed_dataset/gsm8k/test.jsonl',
        'test_cases': [0, 1, 2],  # 使用前3个测试用例
        'raw_data': 0,
        'answer': 'test_answer'
    }
    
    # 使用异步方式运行测试
    async def test():
        score = await _compute_score_async('gsm8k', test_solution, "default", test_extra_info)
        print(f"Test score: {score}")
    
    asyncio.run(test())