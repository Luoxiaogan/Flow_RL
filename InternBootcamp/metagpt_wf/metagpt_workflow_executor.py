#!/usr/bin/env python3
"""
MetaGPT Workflow执行脚本 - 改进版
读取数据集并执行MetaGPT workflow测试：生成通用的workflow模板和验证模型解答
"""

import os
import sys
import json
import re
import asyncio
import importlib.util
from typing import Dict, List, Any, Optional

# 导入配置
from config import LLM_CONFIG, PATHS, EXECUTION_CONFIG, WORKFLOW_TEMPLATE_CONFIG, VERIFICATION_CONFIG

def setup_llm_client():
    """设置LLM客户端"""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=LLM_CONFIG["api_key"],
            base_url=LLM_CONFIG["base_url"]
        )
        return client
    except ImportError:
        print("需要安装openai库: pip install openai")
        return None

def convert_config_for_metagpt(config_dict: Dict) -> object:
    """将我们的配置字典转换为 MetaGPT 期望的配置对象"""
    try:
        from metagpt.provider.llm_provider_registry import LLMType
        from metagpt.configs.llm_config import LLMConfig
        
        # 将 provider 映射到 api_type (使用LLMType枚举)
        provider = config_dict.get('provider', 'openai')
        if provider in ['openai', 'dashscope', 'aliyun_dashscope']:
            # 通义千问API使用OpenAI兼容格式，所以使用OPENAI类型
            api_type = LLMType.OPENAI
        elif provider == 'dashscope_native':
            # 如果需要原生dashscope支持
            api_type = LLMType.DASHSCOPE
        else:
            # 尝试匹配其他提供商
            provider_mapping = {
                'anthropic': LLMType.ANTHROPIC,
                'claude': LLMType.CLAUDE,
                'azure': LLMType.AZURE,
                'gemini': LLMType.GEMINI,
                'moonshot': LLMType.MOONSHOT,
                'qianfan': LLMType.QIANFAN,
                'zhipuai': LLMType.ZHIPUAI,
            }
            api_type = provider_mapping.get(provider, LLMType.OPENAI)
        
        # 创建 LLMConfig 实例
        llm_config = LLMConfig(
            api_type=api_type,
            model=config_dict.get('model'),
            api_key=config_dict.get('api_key'),
            base_url=config_dict.get('base_url'),
            # 可选属性
            temperature=config_dict.get('temperature', 0.7),
            max_token=config_dict.get('max_tokens', 4096),
            timeout=config_dict.get('timeout', 60),
            calc_usage=config_dict.get('calc_usage', True),
            use_system_prompt=config_dict.get('use_system_prompt', True),
            proxy=config_dict.get('proxy', None),
            pricing_plan=config_dict.get('pricing_plan', None),
        )
        
        return llm_config
        
    except ImportError as e:
        print(f"无法导入MetaGPT模块: {e}")
        # 创建简单的mock配置
        class MockLLMConfig:
            def __init__(self):
                self.api_type = "openai"
                self.model = config_dict.get('model')
                self.api_key = config_dict.get('api_key')
                self.base_url = config_dict.get('base_url')
                self.temperature = config_dict.get('temperature', 0.7)
                self.max_token = config_dict.get('max_tokens', 4096)
                self.timeout = config_dict.get('timeout', 60)
        
        return MockLLMConfig()

def load_dataset(dataset_file: str) -> List[Dict]:
    """从JSONL文件加载数据集"""
    dataset = []
    try:
        with open(dataset_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    dataset.append(json.loads(line))
        print(f"成功加载数据集: {len(dataset)} 个任务")
        return dataset
    except Exception as e:
        print(f"加载数据集失败: {e}")
        return []

def create_verification_bootcamps():
    """创建通用的验证系统"""
    
    class GenericBootcamp:
        @staticmethod
        def extract_output(output):
            """通用的答案提取方法"""
            import re
            # 尝试提取[answer]标签内的内容
            matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
            if matches:
                return matches[-1].strip()
            
            # 如果没有标签，尝试提取最后一行作为答案
            lines = output.strip().split('\n')
            if lines:
                return lines[-1].strip()
            
            return None
        
        @classmethod
        def _verify_correction(cls, solution, identity):
            """通用的验证方法"""
            if solution is None:
                return False
            
            # 尝试匹配多种可能的答案字段
            expected_values = []
            for key in ['answer', 'solution', 'plain', 'result', 'output']:
                if key in identity:
                    expected_values.append(str(identity[key]).strip())
            
            solution_str = str(solution).strip()
            
            # 精确匹配
            for expected in expected_values:
                if solution_str == expected:
                    return True
            
            # 数值匹配（如果都是数字）
            try:
                solution_num = float(solution_str)
                for expected in expected_values:
                    try:
                        expected_num = float(expected)
                        if abs(solution_num - expected_num) < 1e-6:
                            return True
                    except ValueError:
                        continue
            except ValueError:
                pass
            
            # 包含匹配（解答包含期望答案）
            for expected in expected_values:
                if expected.lower() in solution_str.lower():
                    return True
            
            return False
    
    # 返回通用验证器，可以处理所有任务类型
    return GenericBootcamp()

def generate_metagpt_workflow_template(client, task_description: str, task_type: str) -> str:
    """使用LLM生成MetaGPT workflow模板"""
    
    operators_desc = "\n".join([f"{i+1}. {op}" for i, op in enumerate(WORKFLOW_TEMPLATE_CONFIG["available_operators"])])
    
    user_message = f"""You are tasked with creating a simple workflow template for solving problems based on the given task description.

Task Type: {task_type}
Task Description:
{task_description}

You need to generate a Python workflow class that directly uses LLM to solve problems. The workflow should be simple and avoid complex configurations.

The workflow template should follow this structure:

<graph>
class Workflow:
    def __init__(self, config, problem):
        self.problem = problem
        self.config = config
        # The agent is just the LLM client
        self.agent = create(config)
        # Initialize simple operators
        self.custom = operator.Custom(self.agent, self.problem)
        self.review = operator.Review(self.agent, self.problem)

    async def run_workflow(self):
        \"\"\"
        Simple workflow that directly solves the problem using LLM.
        \"\"\"
        # Use the custom operator to solve the problem
        solution = await self.custom(instruction="Solve this problem step by step and provide a clear answer")
        
        return solution
</graph>

Available operators you can use:
{operators_desc}

Requirements:
1. Keep the workflow simple and direct
2. Don't use complex MetaGPT configurations
3. The config parameter will be a simple object with basic attributes
4. The create() function will return an LLM client
5. Use operators to interact with the LLM for problem solving
6. The output should be enclosed in <graph> tags
7. Focus on getting the LLM to directly compute the answer

Generate the complete workflow template:
"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=EXECUTION_CONFIG["temperature_generation"]
        )
        
        full_response = response.choices[0].message.content.strip()
        
        # 提取 <graph> 标签内的内容
        if WORKFLOW_TEMPLATE_CONFIG["require_graph_tags"] and "<graph>" in full_response and "</graph>" in full_response:
            workflow_template = full_response.split('<graph>')[1].split('</graph>')[0].strip()
        else:
            # 如果没有找到标记，生成一个默认模板
            workflow_template = f"""class Workflow:
    def __init__(self, config, problem):
        self.problem = problem
        self.config = config
        self.agent = create(config)
        self.custom = operator.Custom(self.agent, self.problem)
        self.review = operator.Review(self.agent, self.problem)

    async def run_workflow(self):
        \"\"\"
        Simple workflow for {task_type} tasks.
        \"\"\"
        solution = await self.custom(instruction="Solve this {task_type} problem step by step with clear reasoning. Provide your final answer.")
        
        return solution"""
        
        return workflow_template
        
    except Exception as e:
        print(f"生成MetaGPT workflow模板失败: {e}")
        return f"""class Workflow:
    def __init__(self, config, problem):
        self.problem = problem
        self.config = config
        self.agent = create(config)
        self.custom = operator.Custom(self.agent, self.problem)

    async def run_workflow(self):
        \"\"\"
        Default workflow for {task_type} tasks.
        \"\"\"
        solution = await self.custom(instruction="Solve this problem step by step and provide the final answer")
        return solution"""

def create_mock_operators():
    """创建模拟的operators用于执行workflow"""
    
    class MockOperator:
        def __init__(self, llm_client, problem):
            self.llm_client = llm_client
            self.problem = problem
    
    class Custom(MockOperator):
        async def __call__(self, instruction: str) -> str:
            try:
                answer_tags = VERIFICATION_CONFIG["answer_tags"]
                response = self.llm_client.chat.completions.create(
                    model=LLM_CONFIG["model"],
                    messages=[
                        {"role": "system", "content": f"You are solving this problem: {self.problem}\n\nInstruction: {instruction}"},
                        {"role": "user", "content": f"Problem: {self.problem}\n\nPlease solve this problem and provide your answer in {answer_tags[0]}...{answer_tags[1]} tags."}
                    ],
                    temperature=EXECUTION_CONFIG["temperature_execution"]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"Error in Custom operator: {e}"
    
    class Review(MockOperator):
        async def __call__(self, pre_solution: str) -> str:
            try:
                answer_tags = VERIFICATION_CONFIG["answer_tags"]
                response = self.llm_client.chat.completions.create(
                    model=LLM_CONFIG["model"],
                    messages=[
                        {"role": "system", "content": "Review and improve the given solution if needed."},
                        {"role": "user", "content": f"Problem: {self.problem}\n\nPrevious solution: {pre_solution}\n\nPlease review this solution and provide the final answer in {answer_tags[0]}...{answer_tags[1]} tags."}
                    ],
                    temperature=EXECUTION_CONFIG["temperature_execution"]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return pre_solution  # 如果review失败，返回原解答
    
    class Programmer(MockOperator):
        async def __call__(self, analysis: str = 'None') -> str:
            try:
                answer_tags = VERIFICATION_CONFIG["answer_tags"]
                prompt = f"Problem: {self.problem}\n"
                if analysis != 'None':
                    prompt += f"Analysis: {analysis}\n"
                prompt += f"Write and execute Python code to solve this problem. Provide your final answer in {answer_tags[0]}...{answer_tags[1]} tags."
                
                response = self.llm_client.chat.completions.create(
                    model=LLM_CONFIG["model"],
                    messages=[
                        {"role": "system", "content": "You are a programming assistant. Write Python code to solve problems."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=EXECUTION_CONFIG["temperature_execution"]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"Error in Programmer operator: {e}"
    
    class ScEnsemble(MockOperator):
        async def __call__(self, solutions: List[str]) -> str:
            try:
                answer_tags = VERIFICATION_CONFIG["answer_tags"]
                solutions_text = "\n\n".join([f"Solution {i+1}: {sol}" for i, sol in enumerate(solutions)])
                response = self.llm_client.chat.completions.create(
                    model=LLM_CONFIG["model"],
                    messages=[
                        {"role": "system", "content": "Select and refine the best solution from the given options."},
                        {"role": "user", "content": f"Problem: {self.problem}\n\nSolutions:\n{solutions_text}\n\nSelect the best solution and provide the final answer in {answer_tags[0]}...{answer_tags[1]} tags."}
                    ],
                    temperature=EXECUTION_CONFIG["temperature_execution"]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return solutions[0] if solutions else "No solution available"
    
    # 返回包含所有operator类的模块对象
    class OperatorModule:
        pass
    
    operator_module = OperatorModule()
    operator_module.Custom = Custom
    operator_module.Review = Review
    operator_module.Programmer = Programmer
    operator_module.ScEnsemble = ScEnsemble
    
    return operator_module

async def execute_metagpt_workflow(workflow_template: str, problem: str, llm_client) -> str:
    """执行MetaGPT workflow - 简化版，直接使用LLM计算"""
    try:
        # 准备执行环境
        operator_module = create_mock_operators()
        
        # 简化的create函数，直接返回LLM客户端
        def create(config):
            return llm_client
        
        # 创建简单的配置对象，只包含必要信息
        class SimpleConfig:
            def __init__(self):
                self.model = LLM_CONFIG["model"]
                self.api_key = LLM_CONFIG["api_key"]
                self.base_url = LLM_CONFIG["base_url"]
        
        config = SimpleConfig()
        
        # 创建完整的workflow代码
        full_code = f"""
import asyncio
from typing import List

{workflow_template}
"""
        
        # 创建执行命名空间，包含所有必要的变量
        execution_globals = {
            'operator': operator_module,
            'create': create,
            'asyncio': asyncio,
            'List': List,
            # 直接添加operator类到命名空间以防workflow模板直接引用
            'Custom': operator_module.Custom,
            'Review': operator_module.Review,
            'Programmer': operator_module.Programmer,
            'ScEnsemble': operator_module.ScEnsemble,
        }
        
        execution_namespace = {}
        exec(full_code, execution_globals, execution_namespace)
        
        # 创建workflow实例并执行
        workflow_class = execution_namespace['Workflow']
        workflow_instance = workflow_class(config=config, problem=problem)
        result = await workflow_instance.run_workflow()
        
        return result
        
    except Exception as e:
        print(f"执行MetaGPT workflow失败: {e}")
        # 如果workflow执行失败，直接用LLM解答
        if VERIFICATION_CONFIG["fallback_on_error"]:
            try:
                answer_tags = VERIFICATION_CONFIG["answer_tags"]
                response = llm_client.chat.completions.create(
                    model=LLM_CONFIG["model"],
                    messages=[
                        {"role": "user", "content": f"Solve this problem: {problem}\n\nProvide your answer in {answer_tags[0]}...{answer_tags[1]} tags."}
                    ],
                    temperature=EXECUTION_CONFIG["temperature_execution"]
                )
                return response.choices[0].message.content.strip()
            except:
                return f"Failed to solve: {problem}"
        else:
            return f"Workflow execution failed: {e}"

def verify_solution(bootcamp, solution: str, case_data: Dict) -> bool:
    """验证解答正确性"""
    try:
        # 提取解答
        extracted = bootcamp.extract_output(solution)
        if extracted is None:
            return False
        
        # 验证正确性
        return bootcamp._verify_correction(extracted, case_data)
    except Exception as e:
        print(f"验证解答时出错: {e}")
        return False

async def process_single_task(client, task_data: Dict, bootcamp):
    """处理单个任务"""
    task_id = task_data["id"]
    task_name = task_data["task_name"]
    task_description = task_data["task_description"]
    test_cases = task_data["test_cases"]
    
    print(f"\n处理任务 {task_id}: {task_name}")
    
    # 1. 生成MetaGPT workflow模板
    print("  生成MetaGPT workflow模板...")
    workflow_template = generate_metagpt_workflow_template(client, task_description, task_name)
    
    # 2. 对每个测试用例执行workflow
    case_results = []
    
    for i, case in enumerate(test_cases):
        print(f"  执行测试用例 {i+1}/{len(test_cases)}...")
        
        # 执行workflow
        solution = await execute_metagpt_workflow(workflow_template, case["prompt"], client)
        
        # 验证结果
        is_correct = False
        if VERIFICATION_CONFIG["enable_verification"]:
            is_correct = verify_solution(bootcamp, solution, case)
        
        case_results.append({
            "case_id": i,
            "prompt": case["prompt"],
            "solution": solution,
            "is_correct": is_correct,
            "expected": case.get("answer") or case.get("solution") or case.get("plain") or case.get("result", "")
        })
    
    # 计算准确率
    correct_count = sum(1 for r in case_results if r["is_correct"])
    accuracy = correct_count / len(case_results) if case_results else 0
    
    result = {
        "task_id": task_id,
        "task_name": task_name,
        "task_description": task_description,
        "workflow_template": workflow_template,
        "test_results": case_results,
        "accuracy": accuracy,
        "correct_count": correct_count,
        "total_count": len(case_results)
    }
    
    print(f"  任务完成，准确率: {accuracy:.2%} ({correct_count}/{len(case_results)})")
    return result

async def main():
    """主函数"""
    # 设置路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_file = os.path.join(current_dir, PATHS["dataset_file"])
    output_file = os.path.join(current_dir, PATHS["output_file"])
    
    # 初始化
    client = setup_llm_client()
    if not client:
        return
    
    # 创建通用验证器
    bootcamp = create_verification_bootcamps()
    
    # 加载数据集
    dataset = load_dataset(dataset_file)
    if not dataset:
        return
    
    print(f"开始处理 {len(dataset)} 个任务...")
    
    # 使用配置的最大并发数限制并行任务
    semaphore = asyncio.Semaphore(EXECUTION_CONFIG["max_concurrent_tasks"])
    
    async def process_with_semaphore(task_data):
        async with semaphore:
            return await process_single_task(client, task_data, bootcamp)
    
    # 并行处理任务
    tasks = [process_with_semaphore(task_data) for task_data in dataset]
    results = await asyncio.gather(*tasks)
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    # 统计总体结果
    total_correct = sum(r["correct_count"] for r in results)
    total_cases = sum(r["total_count"] for r in results)
    overall_accuracy = total_correct / total_cases if total_cases > 0 else 0
    
    print(f"\n=== 总体结果 ===")
    print(f"总任务数: {len(results)}")
    print(f"总测试用例: {total_cases}")
    print(f"总正确数: {total_correct}")
    print(f"总体准确率: {overall_accuracy:.2%}")
    print(f"结果已保存到: {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 