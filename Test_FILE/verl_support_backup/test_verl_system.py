"""
VERL系统全流程模型执行测试脚本
完全模仿现有工作流系统 - 生成数据 -> 模型生成工作流 -> 实际执行模型推理 -> 计算奖励 -> JSON保存
"""
import os
import sys
import json
import logging
import asyncio
import pandas as pd
from datetime import datetime
import importlib
import tempfile
from typing import Dict, List, Any, Tuple
from openai import AsyncOpenAI
import numpy as np

# --- 设置Python路径 - 完全按照workflow_executor.py ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCOREFLOW_PATH = os.path.dirname(CURRENT_DIR)
if SCOREFLOW_PATH not in sys.path:
    sys.path.append(SCOREFLOW_PATH)

# 导入 - 完全按照workflow_executor.py
from metagpt.provider.llm_provider_registry import create_llm_instance, LLMType
from metagpt.configs.llm_config import LLMConfig

from ScoreFlow.scripts.base_handler import BenchmarkHandler

# 本地导入
from utils import load_config, get_benchmark_handler
from workflow_reward import WorkflowRewardCalculator, compute_score

class VerlFullModelExecutionTest:
    """VERL全流程模型执行测试类 - 完全模仿现有系统架构"""
    
    def __init__(self):
        self.config = None
        self.calculator = None
        self.api_configs = None
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {},
            'summary': {},
            'model_execution_logs': []
        }
        
    def setup(self):
        """初始化设置 - 完全按照现有系统"""
        # 加载配置
        self.config = load_config()
        print(f"✅ 配置加载成功: {list(self.config['benchmarks'].keys())}")
        
        # 创建计算器
        self.calculator = WorkflowRewardCalculator(self.config)
        
        # 准备API配置 - 按照workflow_generator.py格式
        self.api_configs = [self.config['api_config']]  # 转换为列表格式
        
        print("✅ 组件初始化成功")
        
        return True
    
    def load_existing_test_data(self):
        """加载已存在的测试数据，不重新生成"""
        print("\n=== 加载现有测试数据 ===")
        
        loaded_benchmarks = []
        data_dir = '/home/lg/workflow_tooluse/Flow_RL/Test_FILE/verl_support/data'
        
        for benchmark_name in self.config['benchmarks'].keys():
            print(f"\n检查 {benchmark_name} 数据...")
            
            # 检查训练数据文件
            train_file = os.path.join(data_dir, f'{benchmark_name}_verl_train.parquet')
            test_file = os.path.join(data_dir, f'{benchmark_name}_verl_test.parquet')
            
            if os.path.exists(train_file) and os.path.exists(test_file):
                # 加载训练数据获取基本信息
                train_df = pd.read_parquet(train_file)
                test_df = pd.read_parquet(test_file)
                
                print(f"✅ {benchmark_name} 数据加载成功:")
                print(f"   训练数据: {len(train_df)} 条")
                print(f"   测试数据: {len(test_df)} 条")
                
                loaded_benchmarks.append(benchmark_name)
                
                # 处理sample_data，确保JSON可序列化
                sample_data = None
                if len(train_df) > 0:
                    sample_row = train_df.iloc[0].to_dict()
                    # 转换numpy类型为Python原生类型
                    sample_data = self._convert_to_json_serializable(sample_row)
                
                # 保存benchmark信息
                self.test_results['benchmarks'][benchmark_name] = {
                    'training_data_count': len(train_df),
                    'test_data_count': len(test_df),
                    'sample_data': sample_data,
                    'data_file_path': test_file,
                    'workflow_generation': None,
                    'model_execution': None,
                    'test_result': None
                }
            else:
                missing_files = []
                if not os.path.exists(train_file):
                    missing_files.append(train_file)
                if not os.path.exists(test_file):
                    missing_files.append(test_file)
                print(f"❌ {benchmark_name} 数据文件缺失: {missing_files}")
        
        self.test_results['summary']['loaded_benchmarks'] = loaded_benchmarks
        print(f"\n总计加载 {len(loaded_benchmarks)} 个benchmark的数据")
        return len(loaded_benchmarks) > 0

    def _convert_to_json_serializable(self, obj):
        """将对象转换为JSON可序列化的格式"""
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
            return str(obj)
        elif hasattr(obj, 'item'):  # Other numpy scalars
            return obj.item()
        else:
            return obj

    async def call_openai_compatible_api(self, api_config: dict, messages: list) -> str:
        """完全复用workflow_generator.py的API调用函数"""
        client = AsyncOpenAI(
            api_key=api_config.get("api_key"), 
            base_url=api_config.get("base_url")
        )
        completion = await client.chat.completions.create(
            model=api_config.get("model"), 
            messages=messages
        )
        return completion.choices[0].message.content
    
    def _load_prompt_templates(self, benchmark_name: str):
        """完全复用workflow_generator.py的模板加载函数"""
        try:
            # Debug: Print the module path being attempted
            module_path = f"ScoreFlow.scripts.{benchmark_name.upper()}.conditions"
            print(f"  🔍 尝试导入模块: {module_path}")
            print(f"  🔍 当前Python路径: {sys.path}")
            print(f"  🔍 SCOREFLOW_PATH: {SCOREFLOW_PATH}")
            
            # Check if ScoreFlow directory exists
            scoreflow_dir = os.path.join(SCOREFLOW_PATH, 'ScoreFlow')
            print(f"  🔍 ScoreFlow目录存在: {os.path.exists(scoreflow_dir)}")
            
            if os.path.exists(scoreflow_dir):
                scripts_dir = os.path.join(scoreflow_dir, 'scripts')
                print(f"  🔍 scripts目录存在: {os.path.exists(scripts_dir)}")
                
                if os.path.exists(scripts_dir):
                    benchmark_dir = os.path.join(scripts_dir, benchmark_name.upper())
                    print(f"  🔍 {benchmark_name.upper()}目录存在: {os.path.exists(benchmark_dir)}")
                    
                    if os.path.exists(benchmark_dir):
                        conditions_file = os.path.join(benchmark_dir, 'conditions.py')
                        print(f"  🔍 conditions.py文件存在: {os.path.exists(conditions_file)}")
        
            conditions_module = importlib.import_module(module_path)
            print(f"  ✅ 模块导入成功")
            
        except ImportError as e:
            print(f"  ❌ 模块导入失败: {e}")
            print(f"  🔧 使用默认模板...")
            
            # Return default templates if import fails
            return (
                "Please solve the following problem step by step:\n\n",
                "\n\nProvide your answer in the required format.",
                "You are a helpful AI assistant that solves problems step by step.",
                ["Think carefully and solve this step by step."]
            )
            
        return (
            getattr(conditions_module, "START_PROMPT", ""), 
            getattr(conditions_module, "END_PROMPT", ""),
            getattr(conditions_module, "SYSTEM_PROMPT", "You are a helpful AI assistant."),
            getattr(conditions_module, "META_PROMPTS", [])
        )

    def _construct_generation_prompt(self, handler, data_indices: list, benchmark_name: str):
        """完全复用workflow_generator.py的prompt构建函数"""
        start_prompt, end_prompt, system_prompt, meta_prompts = self._load_prompt_templates(benchmark_name)
        
        # 1. 使用 handler 获取问题文本
        problem_text = handler.get_prompt_text(data_indices)
        
        # 2. 构建 Prompt
        import random
        selected_meta_prompt = random.choice(meta_prompts) if meta_prompts else ""
        final_end_prompt = f"\n**CRITICAL INSTRUCTION FOR THIS SPECIFIC TASK:**\n{selected_meta_prompt}\n\n" + end_prompt
        user_prompt_str = start_prompt + f"{problem_text}" + final_end_prompt

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt_str}
        ]
        
        return messages, problem_text

    async def generate_workflow_with_model(self, benchmark_name: str, test_index: int):
        """使用模型生成工作流代码 - 完全按照workflow_generator.py逻辑"""
        # 获取handler - 完全按照现有系统
        handler = get_benchmark_handler(
            benchmark_name, 
            self.config['benchmarks'][benchmark_name]['dataset_path']
        )
        
        # 构建生成prompt - 完全复用workflow_generator.py逻辑
        data_indices = [test_index]  # 使用单个测试索引
        messages, problem_text = self._construct_generation_prompt(
            handler, data_indices, benchmark_name
        )
        
        # 调用API - 完全复用workflow_generator.py的函数
        print(f"  🤖 调用模型生成 {benchmark_name} 工作流...")
        api_config = self.api_configs[0]  # 使用第一个API配置
        
        response_content = await self.call_openai_compatible_api(api_config, messages)
        
        # 提取代码 - 完全按照workflow_generator.py逻辑
        if "<graph>" in response_content:
            code = response_content.split('<graph>')[1].split('</graph>')[0].strip()
        else:
            code = response_content.strip().strip('```python').strip('```').strip()
        
        if code:
            print(f"  ✅ 工作流生成成功，代码长度: {len(code)} 字符")
            return code, None
        else:
            raise ValueError("API响应中未能提取有效代码。")
    
    async def execute_workflow_directly(self, py_path: str):
        """直接执行工作流文件，不隐藏任何错误"""
        print(f"  🔧 直接执行工作流文件: {py_path}")
        
        # 标准化路径，移除重复的路径段
        normalized_path = os.path.normpath(py_path)
        print(f"  📍 标准化后路径: {normalized_path}")
        
        # 检查文件是否实际存在
        if not os.path.exists(normalized_path):
            print(f"  ❌ 文件不存在: {normalized_path}")
            print(f"  🔍 检查目录内容:")
            
            # 检查父目录
            parent_dir = os.path.dirname(normalized_path)
            if os.path.exists(parent_dir):
                print(f"  📁 父目录存在: {parent_dir}")
                files = os.listdir(parent_dir)
                print(f"  📋 父目录内容: {files}")
            else:
                print(f"  ❌ 父目录不存在: {parent_dir}")
                
            return False, f"工作流文件不存在: {normalized_path}"
        
        print(f"  ✅ 文件存在，开始执行...")
        
        import subprocess
        import sys
        
        try:
            # 获取文件的绝对路径和目录
            abs_path = os.path.abspath(normalized_path)
            work_dir = os.path.dirname(abs_path)
            
            print(f"  📂 工作目录: {work_dir}")
            print(f"  📄 执行文件: {abs_path}")
            
            result = subprocess.run(
                [sys.executable, abs_path],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=work_dir  # 使用文件所在目录作为工作目录
            )
            
            print(f"  📤 返回码: {result.returncode}")
            
            if result.stdout:
                print(f"  📋 标准输出:")
                print("  " + "="*50)
                for line in result.stdout.split('\n'):
                    if line.strip():
                        print(f"  STDOUT: {line}")
                print("  " + "="*50)
            
            if result.stderr:
                print(f"  ❌ 标准错误:")
                print("  " + "="*50)
                for line in result.stderr.split('\n'):
                    if line.strip():
                        print(f"  STDERR: {line}")
                print("  " + "="*50)
            
            return result.returncode == 0, result.stderr if result.returncode != 0 else None
            
        except subprocess.TimeoutExpired:
            error_msg = "工作流执行超时 (120秒)"
            print(f"  ⏰ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"执行过程中发生异常: {str(e)}"
            print(f"  💥 {error_msg}")
            raise  # 直接抛出异常，不隐藏

    async def execute_workflow_with_model(self, workflow_code: str, benchmark_name: str, test_index: int):
        """使用模型执行工作流 - 显示完整错误信息"""
        print(f"  🚀 开始执行 {benchmark_name} 工作流...")
        
        # 创建临时工作流文件
        workflow_id = f"test_{benchmark_name}_{test_index}"
        dataset_path = self.config['benchmarks'][benchmark_name]['dataset_path']
        
        print(f"  🔧 创建临时工作流文件...")
        print(f"  📊 workflow_id: {workflow_id}")
        print(f"  📊 benchmark_name: {benchmark_name}")
        print(f"  📊 dataset_path: {dataset_path}")
        print(f"  📊 test_indices: {[test_index]}")
        
        py_path, meta_path = self.calculator.create_temporary_workflow_files(
            workflow_code, workflow_id, benchmark_name, dataset_path, [test_index]
        )
        
        print(f"  📁 返回的py_path: {py_path}")
        print(f"  📁 返回的meta_path: {meta_path}")
        
        # 标准化路径
        py_path = os.path.normpath(py_path)
        meta_path = os.path.normpath(meta_path)
        
        print(f"  📍 标准化py_path: {py_path}")
        print(f"  📍 标准化meta_path: {meta_path}")
        
        # 检查文件是否存在
        py_exists = os.path.exists(py_path)
        meta_exists = os.path.exists(meta_path)
        
        print(f"  🔍 py文件存在: {py_exists}")
        print(f"  🔍 meta文件存在: {meta_exists}")
        
        if not py_exists:
            print(f"  ❌ Python文件不存在，检查可能的路径...")
            # 尝试查找可能的文件位置
            possible_dirs = [
                os.path.dirname(py_path),
                os.path.join(CURRENT_DIR, 'temp_workspace', 'temp_workflows', benchmark_name),
                os.path.join(CURRENT_DIR, 'temp_workspace'),
            ]
            
            for dir_path in possible_dirs:
                if os.path.exists(dir_path):
                    print(f"  📁 检查目录: {dir_path}")
                    files = os.listdir(dir_path)
                    print(f"    内容: {files}")
        
        if py_exists:
            print(f"  📋 生成的工作流代码预览:")
            print("  " + "="*50)
            with open(py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for i, line in enumerate(lines[:15], 1):  # 显示前15行
                    print(f"  {i:2d}: {line}")
                if len(lines) > 15:
                    print(f"  ... (还有 {len(lines) - 15} 行)")
            print("  " + "="*50)
            
            # 使用直接执行方法
            print(f"  🔧 使用直接执行方式...")
            success, error_msg = await self.execute_workflow_directly(py_path)
            
            if success:
                status = "verified_correct"
                print(f"  ✅ 工作流执行成功")
            else:
                status = "execution_failed"
                print(f"  ❌ 工作流执行失败")
        else:
            status = "execution_failed"
            error_msg = f"临时工作流文件不存在: {py_path}"
            success = False
        
        # 保留文件用于调试
        print(f"  🗃️ 临时文件保留用于调试: {py_path}")
        
        return status, error_msg
    
    async def test_full_model_execution_per_benchmark(self):
        """为每个benchmark进行完整的模型执行测试"""
        print("\n=== 完整模型执行测试 ===")
        
        tested_benchmarks = []
        for benchmark_name in self.test_results['benchmarks'].keys():
            print(f"\n🔄 开始测试 {benchmark_name}...")
            
            # 检查数据文件是否存在
            data_file_path = self.test_results['benchmarks'][benchmark_name].get('data_file_path')
            
            if data_file_path and os.path.exists(data_file_path):
                print(f"  ✅ 找到测试数据文件: {data_file_path}")
                
                # 加载一个测试索引
                test_indices = self.calculator.load_test_indices(benchmark_name)[:1]
                
                if test_indices:
                    test_index = test_indices[0]
                    print(f"  使用测试索引: {test_index}")
                    
                    # 1. 模型生成工作流
                    workflow_code, gen_error = await self.generate_workflow_with_model(
                        benchmark_name, test_index
                    )
                    
                    if workflow_code:
                        self.test_results['benchmarks'][benchmark_name]['workflow_generation'] = {
                            'success': True,
                            'code_length': len(workflow_code),
                            'code_preview': workflow_code[:200] + "..." if len(workflow_code) > 200 else workflow_code
                        }
                        
                        # 2. 模型执行工作流
                        execution_status, exec_error = await self.execute_workflow_with_model(
                            workflow_code, benchmark_name, test_index
                        )
                        
                        self.test_results['benchmarks'][benchmark_name]['model_execution'] = {
                            'status': execution_status,
                            'error': exec_error,
                            'success': execution_status == "verified_correct"
                        }
                        
                        # 3. 计算奖励分数
                        reward = await self.calculator.compute_workflow_reward(
                            workflow_code, [test_index], benchmark_name
                        )
                        
                        print(f"  ✅ 奖励计算完成: {reward:.4f}")
                        
                        # 保存测试结果
                        self.test_results['benchmarks'][benchmark_name]['test_result'] = {
                            'test_index': test_index,
                            'reward_score': reward,
                            'execution_status': execution_status,
                            'success': execution_status == "verified_correct"
                        }
                        
                        tested_benchmarks.append(benchmark_name)
                        
                    else:
                        self.test_results['benchmarks'][benchmark_name]['workflow_generation'] = {
                            'success': False,
                            'error': gen_error
                        }
                        self.test_results['benchmarks'][benchmark_name]['test_result'] = {
                            'error': f'Workflow generation failed: {gen_error}',
                            'success': False
                        }
                else:
                    print(f"  ❌ 未找到测试索引")
                    self.test_results['benchmarks'][benchmark_name]['test_result'] = {
                        'error': 'No test indices found',
                        'success': False
                    }
            else:
                print(f"  ❌ 数据文件不存在")
                self.test_results['benchmarks'][benchmark_name]['test_result'] = {
                    'error': 'Data file not found',
                    'success': False
                }
        
        self.test_results['summary']['tested_benchmarks'] = tested_benchmarks
        return len(tested_benchmarks) > 0
    
    def save_results_to_json(self):
        """保存结果到JSON文件"""
        print("\n=== 保存测试结果 ===")
        
        # 添加路径信息
        self.test_results['paths'] = {
            'workspace_root': CURRENT_DIR,
            'config_file': os.path.join(CURRENT_DIR, 'config.json'),
            'data_directory': self.config['output_paths']['data_dir'],
            'output_directory': self.config['output_paths'].get('output_dir', 'N/A')
        }
        
        # 添加系统信息
        self.test_results['system_info'] = {
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'script_path': __file__,
            'api_model': self.config['api_config'].get('model', 'N/A')
        }
        
        # 计算总结统计
        total_benchmarks = len(self.test_results['benchmarks'])
        successful_tests = sum(
            1 for b in self.test_results['benchmarks'].values() 
            if b.get('test_result', {}).get('success', False)
        )
        
        successful_generations = sum(
            1 for b in self.test_results['benchmarks'].values()
            if b.get('workflow_generation', {}).get('success', False)
        )
        
        successful_executions = sum(
            1 for b in self.test_results['benchmarks'].values()
            if b.get('model_execution', {}).get('success', False)
        )
        
        self.test_results['summary']['total_benchmarks'] = total_benchmarks
        self.test_results['summary']['successful_tests'] = successful_tests
        self.test_results['summary']['successful_generations'] = successful_generations
        self.test_results['summary']['successful_executions'] = successful_executions
        self.test_results['summary']['success_rate'] = successful_tests / total_benchmarks if total_benchmarks > 0 else 0
        
        # 确保整个结果字典都是JSON可序列化的
        json_serializable_results = self._convert_to_json_serializable(self.test_results)
        
        # 保存到JSON文件
        output_file = os.path.join(CURRENT_DIR, 'verl_full_model_execution_test_results.json')
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_serializable_results, f, indent=2, ensure_ascii=False)
            print(f"✅ 测试结果已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存JSON文件失败: {e}")
            # 尝试保存一个简化版本
            simplified_results = {
                'timestamp': self.test_results['timestamp'],
                'summary': self.test_results['summary'],
                'benchmark_names': list(self.test_results['benchmarks'].keys()),
                'error': f"JSON serialization failed: {str(e)}"
            }
            simplified_file = os.path.join(CURRENT_DIR, 'verl_test_results_simplified.json')
            with open(simplified_file, 'w', encoding='utf-8') as f:
                json.dump(simplified_results, f, indent=2, ensure_ascii=False)
            print(f"⚠️ 已保存简化版结果到: {simplified_file}")
            output_file = simplified_file
        
        return output_file
    
    def print_detailed_results(self):
        """打印详细的测试结果"""
        print(f"\n{'='*60}")
        print("🎯 VERL全流程模型执行测试详细结果")
        print(f"{'='*60}")
        
        # 打印总结
        summary = self.test_results['summary']
        system_info = self.test_results.get('system_info', {})
        print(f"测试时间: {self.test_results['timestamp']}")
        print(f"使用模型: {system_info.get('api_model', 'N/A')}")
        print(f"总benchmark数量: {summary.get('total_benchmarks', 0)}")
        print(f"成功生成工作流: {summary.get('successful_generations', 0)}")
        print(f"成功执行工作流: {summary.get('successful_executions', 0)}")
        print(f"完全成功测试: {summary.get('successful_tests', 0)}")
        print(f"整体成功率: {summary.get('success_rate', 0):.2%}")
        
        # 打印各benchmark详情
        print(f"\n{'='*40}")
        print("📊 各Benchmark模型执行详情")
        print(f"{'='*40}")
        
        for benchmark_name, benchmark_data in self.test_results['benchmarks'].items():
            print(f"\n🔍 {benchmark_name.upper()}")
            print(f"  训练数据条数: {benchmark_data.get('training_data_count', 'N/A')}")
            print(f"  数据文件路径: {benchmark_data.get('data_file_path', 'N/A')}")
            
            # 工作流生成结果
            workflow_gen = benchmark_data.get('workflow_generation', {})
            if workflow_gen and workflow_gen.get('success', False):
                print(f"  ✅ 工作流生成成功")
                print(f"  生成代码长度: {workflow_gen.get('code_length', 0)} 字符")
            else:
                print(f"  ❌ 工作流生成失败")
                if workflow_gen:
                    print(f"  错误: {workflow_gen.get('error', 'Unknown error')}")
            
            # 模型执行结果
            model_exec = benchmark_data.get('model_execution', {})
            if model_exec:
                print(f"  模型执行状态: {model_exec.get('status', 'N/A')}")
                if model_exec.get('success', False):
                    print(f"  ✅ 模型执行成功")
                else:
                    print(f"  ❌ 模型执行失败")
                    if model_exec.get('error'):
                        print(f"  执行错误: {model_exec['error']}")
            
            # 最终测试结果
            test_result = benchmark_data.get('test_result', {})
            if test_result.get('success', False):
                print(f"  ✅ 整体测试成功")
                print(f"  测试索引: {test_result.get('test_index', 'N/A')}")
                print(f"  奖励分数: {test_result.get('reward_score', 0):.4f}")
            else:
                print(f"  ❌ 整体测试失败")
                print(f"  错误信息: {test_result.get('error', 'Unknown error')}")
        
        # 打印路径信息
        if 'paths' in self.test_results:
            print(f"\n{'='*40}")
            print("📁 路径信息")
            print(f"{'='*40}")
            paths = self.test_results['paths']
            for key, path in paths.items():
                print(f"  {key}: {path}")

async def main():
    """主测试函数"""
    print("🚀 开始VERL系统全流程模型执行测试")
    
    # 设置日志级别
    logging.basicConfig(level=logging.WARNING)  # 减少输出噪音
    
    # 创建测试实例
    tester = VerlFullModelExecutionTest()
    
    # 执行全流程测试
    # 1. 初始化
    if not tester.setup():
        print("❌ 初始化失败，退出测试")
        return
    
    # 2. 加载数据
    if not tester.load_existing_test_data():
        print("❌ 数据加载失败，退出测试")
        return
    
    # 3. 完整模型执行测试
    if not await tester.test_full_model_execution_per_benchmark():
        print("❌ 模型执行测试失败，但继续保存结果")
    
    # 4. 保存结果到JSON
    output_file = tester.save_results_to_json()
    
    # 5. 打印详细结果
    tester.print_detailed_results()
    
    # 最终状态
    successful_tests = tester.test_results['summary'].get('successful_tests', 0)
    total_benchmarks = tester.test_results['summary'].get('total_benchmarks', 0)
    
    print(f"\n{'='*60}")
    if successful_tests == total_benchmarks and total_benchmarks > 0:
        print("🎉 全流程模型执行测试完全成功！")
    elif successful_tests > 0:
        print(f"⚠️ 部分测试成功 ({successful_tests}/{total_benchmarks})")
    else:
        print("❌ 全流程模型执行测试失败")
    
    if output_file:
        print(f"📄 详细结果已保存至: {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 