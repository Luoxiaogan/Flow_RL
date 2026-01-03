#!/usr/bin/env python3
"""
Workflow执行脚本 - 改进版
读取数据集并执行workflow测试：生成通用的system_prompt和验证模型解答
"""

import os
import sys
import json
import re
from typing import Dict, List, Any, Optional

# LLM配置
LLM_CONFIG = {
    "provider": "aliyun_dashscope", 
    "model": "qwen-plus",
    "api_key": "sk-2df74af0570a42059c10a3f24de1b9df",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
}

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
    """创建用于验证的bootcamp实例"""
    
    class AAPBootcamp:
        @staticmethod
        def extract_output(output):
            import re
            matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
            if not matches:
                return None
            try:
                return int(matches[-1].strip().split()[0].replace(',', ''))
            except:
                return None
        
        @classmethod
        def _verify_correction(cls, solution, identity):
            return isinstance(solution, int) and solution == identity["ans"]
    
    class Game24Bootcamp:
        @staticmethod
        def extract_output(output):
            import re
            matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
            if not matches:
                return None
            return matches[-1].strip()
        
        @classmethod
        def _verify_correction(cls, solution, identity):
            if not solution:
                return False
            try:
                # 简单验证：检查是否包含所有数字
                numbers = identity["numbers"]
                for num in numbers:
                    if str(num) not in solution:
                        return False
                return True
            except:
                return False
    
    class CipherBootcamp:
        @staticmethod
        def extract_output(output):
            import re
            matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
            if not matches:
                return None
            return matches[-1].strip().upper()
        
        @classmethod
        def _verify_correction(cls, solution, identity):
            return solution == identity["plain"]
    
    class SudokuBootcamp:
        @staticmethod
        def extract_output(output):
            import re
            matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
            if not matches:
                return None
            solution = matches[-1].strip()
            return ''.join(c for c in solution if c.isdigit())
        
        @classmethod
        def _verify_correction(cls, solution, identity):
            return solution == identity["solution"]
    
    return {
        "aalmostarithmeticalprogression": AAPBootcamp(),
        "game24": Game24Bootcamp(),
        "cipher": CipherBootcamp(),
        "sudoku": SudokuBootcamp()
    }

def generate_system_prompt(client, task_description: str, task_type: str) -> str:
    """使用LLM生成通用的system_prompt"""
    
    user_message = f"""You are tasked with creating a professional system prompt for a downstream model to solve problems based on the given task description.

Task Type: {task_type}
Task Description:
{task_description}

Please think step by step about how to create an effective system prompt for this type of problem. Consider:

1. What type of problem-solving approach would be most effective?
2. What key steps should the model follow?
3. What common mistakes should be avoided?
4. What output format requirements should be emphasized?
5. How can the prompt be general enough to work for similar problems?

Think through your approach first, then provide your final system prompt that will guide the downstream model effectively.

Requirements for the system prompt:
- Use clear, professional English
- Provide step-by-step guidance
- Emphasize the required output format with [answer] tags
- Be applicable to similar problems of this type
- Avoid being overly specific to just this one task

Final Prompt:
"""
    
    try:
        response = client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        
        full_response = response.choices[0].message.content.strip()
        
        # 提取 "Final Prompt:" 后面的内容
        if "Final Prompt:" in full_response:
            system_prompt = full_response.split("Final Prompt:")[-1].strip()
        else:
            # 如果没有找到标记，使用整个回复作为后备
            system_prompt = full_response
        
        return system_prompt
        
    except Exception as e:
        print(f"生成system prompt失败: {e}")
        return f"You are a professional problem-solving assistant specialized in {task_type} tasks. Analyze the problem carefully, provide step-by-step reasoning, and format your final answer according to the specified requirements using [answer] tags."

def solve_with_llm(client, system_prompt: str, user_prompt: str) -> str:
    """使用LLM解决问题"""
    try:
        response = client.chat.completions.create(
            model=LLM_CONFIG["model"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM解答失败: {e}")
        return ""

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
        print(f"验证失败: {e}")
        return False

def execute_workflow_on_task(client, task_data: Dict, bootcamps: Dict) -> Dict:
    """对单个任务执行workflow测试"""
    task_name = task_data["task_name"]
    task_type = task_data["task_type"]
    task_description = task_data["task_description"]
    test_cases = task_data["test_cases"]
    
    print(f"\n处理任务: {task_name} ({task_type})")
    
    # 生成system_prompt
    system_prompt = generate_system_prompt(client, task_description, task_type)
    print(f"生成system_prompt: {system_prompt[:100]}...")
    
    # 获取对应的验证bootcamp
    bootcamp = bootcamps.get(task_name)
    if not bootcamp:
        print(f"警告: 未找到任务 {task_name} 的验证bootcamp")
        return None
    
    # 执行测试用例
    test_results = []
    for i, test_case in enumerate(test_cases):
        print(f"  测试用例 {i+1}...")
        
        # 使用下游模型解答
        solution = solve_with_llm(client, system_prompt, test_case["prompt"])
        print(f"    模型解答前50字符: {solution[:50]}...")
        
        # 验证正确性
        is_correct = verify_solution(bootcamp, solution, test_case["case"])
        
        test_result = {
            "test_case_id": i,
            "prompt": test_case["prompt"],
            "solution": solution,
            "is_correct": is_correct,
            "expected_case": test_case["case"]
        }
        
        test_results.append(test_result)
        print(f"    结果: {'✓ 正确' if is_correct else '✗ 错误'}")
    
    return {
        "task_id": task_data["id"],
        "task_name": task_name,
        "task_type": task_type,
        "task_description": task_description,
        "system_prompt": system_prompt,
        "test_results": test_results
    }

def save_results(results: List[Dict], output_file: str):
    """保存结果到JSONL文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

def print_statistics(results: List[Dict]):
    """打印统计信息"""
    print(f"\n{'='*60}")
    print("WORKFLOW测试统计结果 (改进版)")
    print(f"{'='*60}")
    
    total_tasks = len(results)
    total_tests = sum(len(result["test_results"]) for result in results)
    total_correct = sum(sum(1 for tr in result["test_results"] if tr["is_correct"]) 
                       for result in results)
    
    print(f"总任务数: {total_tasks}")
    print(f"总测试用例数: {total_tests}")
    print(f"总正确数: {total_correct}")
    print(f"总体准确率: {total_correct/total_tests*100:.1f}%" if total_tests > 0 else "无有效测试")
    
    print(f"\n{'任务名称':<25} {'类型':<20} {'准确率':<10} {'详情'}")
    print("-" * 70)
    
    for result in results:
        task_name = result["task_name"]
        task_type = result["task_type"]
        test_results = result["test_results"]
        
        correct_count = sum(1 for tr in test_results if tr["is_correct"])
        total_count = len(test_results)
        accuracy = correct_count / total_count * 100 if total_count > 0 else 0
        
        print(f"{task_name:<25} {task_type:<20} {accuracy:>6.1f}%    {correct_count}/{total_count}")

def main():
    """主函数"""
    print("=== WORKFLOW执行脚本 (改进版) ===")
    
    # 检查数据集文件
    dataset_file = "multi_task_dataset.jsonl"
    if not os.path.exists(dataset_file):
        print(f"错误: 数据集文件 {dataset_file} 不存在")
        print("请先运行 generate_dataset.py 生成数据集")
        return
    
    # 设置LLM客户端
    client = setup_llm_client()
    if not client:
        print("LLM客户端设置失败，无法执行workflow测试")
        return
    
    # 加载数据集
    dataset = load_dataset(dataset_file)
    if not dataset:
        return
    
    # 创建验证bootcamp
    bootcamps = create_verification_bootcamps()
    
    # 执行workflow测试
    print(f"\n开始执行workflow测试...")
    results = []
    
    for task_data in dataset:
        result = execute_workflow_on_task(client, task_data, bootcamps)
        if result:
            results.append(result)
    
    # 保存结果
    output_file = "workflow_execution_results_improved.jsonl"
    save_results(results, output_file)
    print(f"\n结果已保存到: {output_file}")
    
    # 打印统计信息
    print_statistics(results)

if __name__ == "__main__":
    main() 