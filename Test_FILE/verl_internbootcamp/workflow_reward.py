"""
工作流奖励计算模块 - VERL兼容版本
提供compute_score等接口用于计算workflow的奖励分数
"""
import os
import sys
import json
import asyncio
import traceback
from typing import List, Dict, Any, Optional, Union
import logging
from pathlib import Path
import tempfile
import time
import importlib.util

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from internbootcamp_utils import InternBootcampManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """工作流执行器 - 使用真实的MetaGPT执行"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化执行器"""
        if config is None:
            config_path = Path(__file__).parent / "config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
        
        self.config = config
        self.timeout = config.get('reward_config', {}).get('timeout', 180)
    
    async def execute_workflow_with_metagpt(self, workflow_code: str, 
                                          problem_data: Dict[str, Any]) -> Optional[str]:
        """使用MetaGPT执行workflow"""
        try:
            # 动态导入MetaGPT组件
            from metagpt.provider.llm_provider_registry import create_llm_instance
            from metagpt.configs.llm_config import LLMConfig, LLMType
        except ImportError as e:
            logger.error(f"MetaGPT not available: {e}")
            raise RuntimeError(f"MetaGPT dependencies not found: {e}. Please ensure MetaGPT is properly installed.")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(workflow_code)
            temp_file = f.name
        
        try:
            # 动态导入workflow
            spec = importlib.util.spec_from_file_location("temp_workflow", temp_file)
            workflow_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(workflow_module)
            
            # 获取workflow类
            workflow_class = getattr(workflow_module, "InternBootcampWorkflow")
            
            # 验证必要的配置
            llm_config_data = self.config.get('llm_config', {}).get('downstream', {})
            api_key = os.getenv("DEEPSEEK_API_KEY", llm_config_data.get('api_key', ''))
            
            if not api_key:
                raise ValueError("API key not found. Please set DEEPSEEK_API_KEY environment variable or configure in config.json")
            
            # 创建LLM实例
            llm_config = LLMConfig(
                api_type=LLMType.OPENAI,
                model=llm_config_data.get('model', 'deepseek-chat'),
                api_key=api_key,
                base_url=llm_config_data.get('base_url', 'https://api.deepseek.com')
            )
            llm = create_llm_instance(llm_config)
            
            # 创建并运行workflow
            workflow = workflow_class(llm)
            result = await asyncio.wait_for(
                workflow.run(problem_data),
                timeout=self.timeout
            )
            
            return str(result)
            
        except asyncio.TimeoutError:
            logger.error(f"Workflow execution timeout after {self.timeout}s")
            raise TimeoutError(f"Workflow execution exceeded timeout of {self.timeout} seconds")
        except Exception as e:
            logger.error(f"Workflow execution error: {e}\n{traceback.format_exc()}")
            raise RuntimeError(f"Workflow execution failed: {e}")
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {cleanup_error}")


class RewardCalculator:
    """奖励计算器"""
    
    def __init__(self):
        """初始化计算器"""
        self.manager = InternBootcampManager()
        self.executor = WorkflowExecutor()
    
    def calculate_single_reward(self, task_name: str, test_case: Dict[str, Any], 
                              workflow_output: str) -> float:
        """计算单个测试用例的奖励"""
        try:
            # 获取bootcamp类
            bootcamp_class = self.manager.get_bootcamp_class(task_name)
            if bootcamp_class is None:
                logger.error(f"Bootcamp class not found for task: {task_name}")
                return 0.0
            
            bootcamp = bootcamp_class()
            
            # 使用bootcamp的verify_score方法
            score = bootcamp.verify_score(workflow_output, test_case)
            return float(score)
            
        except Exception as e:
            logger.error(f"Failed to calculate reward: {e}")
            return 0.0
    
    async def compute_workflow_reward(self, workflow_code: str, task_name: str,
                                    test_cases: Optional[List[Dict[str, Any]]] = None) -> float:
        """计算工作流的平均奖励分数"""
        try:
            # 如果没有提供测试用例，生成新的
            if test_cases is None:
                n_test_cases = 3
                test_cases = self.manager.generate_task_examples(task_name, n_examples=n_test_cases)
            
            if not test_cases:
                logger.error(f"No test cases for task {task_name}")
                return 0.0
            
            # 获取bootcamp类用于生成prompt
            bootcamp_class = self.manager.get_bootcamp_class(task_name)
            if bootcamp_class is None:
                logger.error(f"Bootcamp class not found for task: {task_name}")
                return 0.0
            
            bootcamp = bootcamp_class()
            
            # 执行workflow并计算奖励
            total_reward = 0.0
            valid_count = 0
            failed_executions = []
            
            for i, test_case in enumerate(test_cases):
                try:
                    # 生成problem data
                    problem_prompt = bootcamp.prompt_func(test_case)
                    problem_data = {
                        "input": problem_prompt,
                        "identity": test_case.get("identity", f"test_case_{i}"),
                        **test_case
                    }
                    
                    # 执行workflow
                    workflow_output = await self.executor.execute_workflow_with_metagpt(
                        workflow_code, problem_data
                    )
                    
                    # 计算奖励
                    reward = self.calculate_single_reward(task_name, test_case, workflow_output)
                    total_reward += reward
                    valid_count += 1
                    logger.debug(f"Test case {test_case.get('identity')}: reward={reward}")
                    
                except Exception as e:
                    failed_executions.append(f"Test case {i}: {str(e)}")
                    logger.error(f"Failed to execute workflow for test case {i}: {e}")
            
            # 如果所有执行都失败了，抛出异常
            if valid_count == 0:
                error_msg = f"All workflow executions failed for task {task_name}. Errors: {'; '.join(failed_executions)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            # 返回平均奖励
            avg_reward = total_reward / valid_count
            
            if failed_executions:
                logger.warning(f"Some executions failed ({len(failed_executions)}/{len(test_cases)}): {'; '.join(failed_executions)}")
            
            logger.info(f"Average reward for {task_name}: {avg_reward:.3f} ({valid_count}/{len(test_cases)} successful)")
            return avg_reward
            
        except Exception as e:
            logger.error(f"Failed to compute workflow reward: {e}\n{traceback.format_exc()}")
            raise RuntimeError(f"Workflow reward computation failed: {e}")


# 全局实例
_calculator = None


def get_calculator() -> RewardCalculator:
    """获取全局RewardCalculator实例"""
    global _calculator
    if _calculator is None:
        _calculator = RewardCalculator()
    return _calculator


# VERL兼容接口
async def compute_score(workflow_code: str, task_name: str, 
                       test_cases: Optional[List[Dict[str, Any]]] = None) -> float:
    """
    计算workflow的奖励分数 - VERL兼容接口
    
    Args:
        workflow_code: 完整的workflow Python代码
        task_name: 任务名称
        test_cases: 可选的测试用例列表
    
    Returns:
        float: 平均奖励分数 (0.0-1.0)
    """
    calculator = get_calculator()
    return await calculator.compute_workflow_reward(workflow_code, task_name, test_cases)


async def batch_compute_scores(workflow_codes: List[str], 
                              task_names: Union[str, List[str]],
                              test_cases_list: Optional[List[List[Dict[str, Any]]]] = None) -> List[float]:
    """
    批量计算多个workflow的奖励分数
    
    Args:
        workflow_codes: workflow代码列表
        task_names: 任务名称（单个字符串或列表）
        test_cases_list: 可选的测试用例列表的列表
    
    Returns:
        List[float]: 奖励分数列表
    """
    # 处理task_names参数
    if isinstance(task_names, str):
        task_names = [task_names] * len(workflow_codes)
    
    if len(workflow_codes) != len(task_names):
        raise ValueError("workflow_codes and task_names must have the same length")
    
    # 处理test_cases_list参数
    if test_cases_list is None:
        test_cases_list = [None] * len(workflow_codes)
    elif len(test_cases_list) != len(workflow_codes):
        raise ValueError("test_cases_list must have the same length as workflow_codes")
    
    # 并发计算
    tasks = [
        compute_score(code, name, cases)
        for code, name, cases in zip(workflow_codes, task_names, test_cases_list)
    ]
    
    return await asyncio.gather(*tasks)


# 同步接口（用于非异步环境）
def compute_score_sync(workflow_code: str, task_name: str,
                      test_cases: Optional[List[Dict[str, Any]]] = None) -> float:
    """同步版本的compute_score"""
    return asyncio.run(compute_score(workflow_code, task_name, test_cases))


# 用于VERL训练的辅助函数
def extract_workflow_from_messages(messages: List[Dict[str, str]]) -> Optional[str]:
    """从VERL格式的消息中提取workflow代码"""
    for msg in messages:
        if msg.get("role") == "assistant":
            return msg.get("content")
    return None


async def compute_verl_entry_reward(verl_entry: Dict[str, Any]) -> float:
    """计算VERL数据条目的奖励"""
    # 提取信息
    task_name = verl_entry["reward_model"]["task_name"]
    
    # 从reward_model或messages中提取workflow代码
    workflow_code = verl_entry["reward_model"].get("workflow_code")
    if workflow_code is None:
        workflow_code = extract_workflow_from_messages(verl_entry.get("prompt", []))
    
    if workflow_code is None:
        logger.error("No workflow code found in VERL entry")
        return 0.0
    
    # 获取测试用例（如果有的话）
    test_case_ids = verl_entry["reward_model"].get("test_cases", [])
    
    # 计算奖励
    return await compute_score(workflow_code, task_name)


# 测试代码
if __name__ == "__main__":
    # 测试工作流代码
    test_workflow = """
import asyncio
from metagpt.actions import Action

class InternBootcampWorkflow:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = '''You are an expert problem solver.'''
    
    async def run(self, problem_data):
        # 简单的示例实现
        problem = problem_data.get('input', '')
        
        # 创建Action并执行
        action = Action(llm=self.llm)
        result = await action.run(
            self.system_prompt, 
            f"Solve this problem: {problem}"
        )
        
        return result
"""
    
    async def test():
        # 获取可用任务
        manager = InternBootcampManager()
        available_tasks = manager.get_available_tasks()
        
        if not available_tasks:
            print("No available tasks found")
            return
        
        # 测试第一个任务
        test_task = available_tasks[0]
        print(f"Testing with task: {test_task}")
        
        # 计算奖励
        score = await compute_score(test_workflow, test_task)
        print(f"Reward score: {score:.3f}")
        
        # 测试批量计算
        print("\nTesting batch computation...")
        scores = await batch_compute_scores(
            [test_workflow, test_workflow],
            [test_task, test_task]
        )
        print(f"Batch scores: {scores}")
    
    asyncio.run(test())