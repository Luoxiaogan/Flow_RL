"""
工作流奖励函数 - 严格复用 workflow_executor.py 的执行逻辑
"""
import os
import sys
import asyncio
import tempfile
import json
import logging
import csv
import importlib
from typing import List, Dict, Any, Tuple
import pandas as pd

# 添加必要路径 - 完全按照workflow_executor.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCOREFLOW_PATH = os.path.dirname(CURRENT_DIR)
if SCOREFLOW_PATH not in sys.path:
    sys.path.append(SCOREFLOW_PATH)

# 导入必要模块 - 与 workflow_executor.py 相同
from metagpt.provider.llm_provider_registry import create_llm_instance, LLMType
from metagpt.configs.llm_config import LLMConfig
from utils import get_benchmark_handler, load_config

class WorkflowRewardCalculator:
    """
    工作流奖励计算器
    核心原则：完全复用 workflow_executor.py 的执行逻辑
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.api_config = config['api_config']
        self.temp_workspace = config['output_paths']['temp_workspace']
        
        # 确保临时工作空间存在
        os.makedirs(self.temp_workspace, exist_ok=True)
        
        logging.info("WorkflowRewardCalculator 初始化完成")

    def convert_config_for_metagpt(self, config_dict: Dict) -> LLMConfig:
        """
        与 workflow_executor.py 完全相同的函数
        将字典格式的LLM配置转换为metagpt的LLMConfig对象
        """
        provider = config_dict.get('provider', 'openai')
        api_type_map = {
            'openai': LLMType.OPENAI, 'azure': LLMType.AZURE, 'gemini': LLMType.GEMINI,
            'claude': LLMType.CLAUDE, 'moonshot': LLMType.MOONSHOT,
            'zhipuai': LLMType.ZHIPUAI, 'qianfan': LLMType.QIANFAN,
        }
        api_type = api_type_map.get(provider.lower(), LLMType.OPENAI)
        
        return LLMConfig(
            api_type=api_type,
            model=config_dict.get('model'),
            api_key=config_dict.get('api_key'),
            base_url=config_dict.get('base_url')
        )

    def create_temporary_workflow_files(self, workflow_code: str, workflow_id: str, 
                                      benchmark_name: str, dataset_path: str, 
                                      data_indices: List[int]) -> Tuple[str, str]:
        """
        创建临时的工作流文件 (.py 和 .meta.json)
        复用 workflow_generator.py 的 _save_workflow_files 格式
        """
        # 创建临时文件路径
        workflow_dir = os.path.join(self.temp_workspace, "temp_workflows", benchmark_name)
        os.makedirs(workflow_dir, exist_ok=True)
        
        py_path = os.path.join(workflow_dir, f"{workflow_id}.py")
        meta_path = os.path.join(workflow_dir, f"{workflow_id}.meta.json")
        
        # 保存 .py 文件 (与 workflow_generator.py 格式相同)
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write(f"# Workflow ID: {workflow_id}\n# Benchmark: {benchmark_name}\n# Data Indices: {data_indices}\n\n{workflow_code}")
        
        # 保存 .meta.json 文件 (与 workflow_generator.py 格式相同)
        meta_data = {
            "id": workflow_id,
            "benchmark": benchmark_name,
            "data_indices": data_indices,
            "dataset_path": dataset_path,
            "generation_timestamp": 0  # 临时文件不需要时间戳
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=4)
            
        return py_path, meta_path

    async def execute_single_workflow(self, workflow_path: str, exec_llm_config: Dict, 
                                    workflow_timeout: int = 120) -> Tuple[str, str]:
        """
        执行单个工作流并返回结果
        严格复用 workflow_executor.py 的 execute_and_verify 逻辑
        """
        workflow_id, benchmark_name, status, error_msg = "unknown", "unknown", "initialization_failed", ""
        
        try:
            # 1. 加载元数据 (与 workflow_executor.py 相同)
            meta_path = workflow_path.replace('.py', '.meta.json')
            if not os.path.exists(meta_path):
                raise FileNotFoundError(f"元数据文件未找到: {meta_path}")
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            workflow_id = meta['id']
            benchmark_name = meta['benchmark']
            dataset_path = meta['dataset_path']
            data_indices = meta['data_indices']
            verification_index = data_indices[0]

            # 2. 初始化 Handler 并获取验证所需数据 (与 workflow_executor.py 相同)
            handler = get_benchmark_handler(benchmark_name, dataset_path)
            verification_data = handler.get_verification_data(verification_index)
            
            # 3. 加载工作流代码 (与 workflow_executor.py 相同)
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_code = f.read()
            
            # 4. 使用 Handler 构建完整的可执行脚本 (与 workflow_executor.py 相同)
            full_script_code = handler.build_executable_script(workflow_code, workflow_timeout)
            
            # 5. 准备执行环境并执行脚本 (与 workflow_executor.py 相同)
            execution_namespace = {}
            
            # 动态加载主 operator 模块 (与 workflow_executor.py 相同)
            operator_module = importlib.import_module(f"ScoreFlow.scripts.{benchmark_name.upper()}.operator")
            
            # 准备一个基础的全局命名空间 (与 workflow_executor.py 相同)
            exec_globals = {
                'asyncio': asyncio,
                'create': create_llm_instance,
                'operator': operator_module,
                'Literal': getattr(__import__('typing'), 'Literal'),
                'List': List,
            }

            # 动态检查并注入可选的 operator_an 模块 (与 workflow_executor.py 相同)
            try:
                an_module_path = f"ScoreFlow.scripts.{benchmark_name.upper()}.operator_an"
                operator_an_module = importlib.import_module(an_module_path)
                
                for attr_name in dir(operator_an_module):
                    if not attr_name.startswith('_'):
                        exec_globals[attr_name] = getattr(operator_an_module, attr_name)
            except ModuleNotFoundError:
                pass

            exec(full_script_code, exec_globals, execution_namespace)
            
            WorkflowClass = execution_namespace.get('Workflow')
            if not WorkflowClass:
                raise ValueError("在执行的脚本中未找到 'Workflow' 类。")
            
            metagpt_llm_config = self.convert_config_for_metagpt(exec_llm_config)
            
            # 实例化并运行工作流 (与 workflow_executor.py 相同)
            workflow_instance = WorkflowClass(config=metagpt_llm_config, problem=verification_data)
            execution_result = await workflow_instance()
            
            # 6. 使用 Handler 进行验证 (与 workflow_executor.py 相同)
            is_correct = handler.judge(execution_result, verification_data)
            status = "verified_correct" if is_correct else "verified_incorrect"
            
        except Exception as e:
            status = "execution_failed"
            error_msg = f"{type(e).__name__}: {e}"
            logging.debug(f"工作流 {workflow_id} 执行失败: {e}")

        return status, error_msg

    async def compute_workflow_reward(self, workflow_code: str, test_indices: List[int], 
                                    data_source: str) -> float:
        """
        计算工作流在测试数据上的奖励分数
        返回准确率作为奖励 (0.0 到 1.0)
        """
        if not test_indices:
            logging.warning("测试索引为空，返回0奖励")
            return 0.0
            
        benchmark_config = self.config['benchmarks'][data_source]
        dataset_path = benchmark_config['dataset_path']
        
        correct_count = 0
        total_count = len(test_indices)
        
        # 为每个测试样本创建临时工作流并执行
        for i, test_index in enumerate(test_indices):
            try:
                workflow_id = f"temp_reward_{data_source}_{i}"
                
                # 创建临时工作流文件
                py_path, meta_path = self.create_temporary_workflow_files(
                    workflow_code, workflow_id, data_source, dataset_path, [test_index]
                )
                
                # 执行工作流
                status, error_msg = await self.execute_single_workflow(
                    py_path, self.api_config, workflow_timeout=120
                )
                
                if status == "verified_correct":
                    correct_count += 1
                    
                # 清理临时文件
                if os.path.exists(py_path):
                    os.remove(py_path)
                if os.path.exists(meta_path):
                    os.remove(meta_path)
                    
            except Exception as e:
                logging.debug(f"测试样本 {test_index} 执行出错: {e}")
                continue
        
        # 计算准确率作为奖励
        reward = correct_count / total_count if total_count > 0 else 0.0
        logging.info(f"工作流奖励计算完成: {correct_count}/{total_count} = {reward:.3f}")
        
        return reward

    def load_test_indices(self, data_source: str) -> List[int]:
        """从测试集文件中加载测试索引"""
        test_file_path = os.path.join(
            self.config['output_paths']['data_dir'],
            f"{data_source}_verl_test.parquet"
        )
        
        if not os.path.exists(test_file_path):
            raise FileNotFoundError(f"测试集文件未找到: {test_file_path}")
            
        test_df = pd.read_parquet(test_file_path)
        return test_df['test_index'].tolist()


# === 参考 math.py 格式的简化接口函数 ===

def compute_score(workflow_code: str, data_source: str, 
                 config_path: str = None) -> float:
    """
    参考 math.py 中 compute_score 函数的简化接口
    
    Args:
        workflow_code: 生成的工作流代码
        data_source: 数据集名称 (如 'gsm8k', 'mbpp')
        config_path: 配置文件路径
        
    Returns:
        float: 奖励分数 (0.0 到 1.0)
    """
    try:
        # 加载配置
        config = load_config(config_path)
        
        # 创建奖励计算器
        calculator = WorkflowRewardCalculator(config)
        
        # 加载测试集索引
        test_indices = calculator.load_test_indices(data_source)
        
        # 计算奖励 (异步运行)
        reward = asyncio.run(calculator.compute_workflow_reward(
            workflow_code, test_indices, data_source
        ))
        
        return reward
        
    except Exception as e:
        logging.error(f"计算工作流奖励时出错: {e}")
        return 0.0


# === 批量测试函数 ===

async def batch_compute_rewards(workflow_codes: List[str], data_source: str, 
                               config_path: str = None) -> List[float]:
    """
    批量计算多个工作流的奖励分数
    
    Args:
        workflow_codes: 工作流代码列表
        data_source: 数据集名称
        config_path: 配置文件路径
        
    Returns:
        List[float]: 奖励分数列表
    """
    config = load_config(config_path)
    calculator = WorkflowRewardCalculator(config)
    test_indices = calculator.load_test_indices(data_source)
    
    rewards = []
    for i, workflow_code in enumerate(workflow_codes):
        try:
            reward = await calculator.compute_workflow_reward(
                workflow_code, test_indices, data_source
            )
            rewards.append(reward)
            logging.info(f"工作流 {i+1}/{len(workflow_codes)} 奖励: {reward:.3f}")
        except Exception as e:
            logging.error(f"计算工作流 {i+1} 奖励时出错: {e}")
            rewards.append(0.0)
    
    return rewards


if __name__ == "__main__":
    # 简单测试
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 示例工作流代码 (这里需要真实的工作流代码)
    test_workflow_code = """
class Workflow:
    def __init__(self, config, problem):
        self.config = config
        self.problem = problem

    async def __call__(self):
        # 简单的示例实现
        return "42"
"""
    
    try:
        score = compute_score(test_workflow_code, "gsm8k")
        print(f"测试工作流奖励分数: {score}")
    except Exception as e:
        print(f"测试失败: {e}") 