#!/usr/bin/env python3
"""
数据集处理脚本 - 改进版
从internbootcamp中动态选择多个任务，提取真实的任务描述并生成测试用例
"""

import os
import sys
import json
import re
import importlib
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'internbootcamp'))

def extract_task_description_from_source(source_code: str) -> Optional[str]:
    """从源代码中提取任务描述（到'Here is a reference code'之前）"""
    try:
        # 查找文档字符串中的任务描述
        if '"""' in source_code:
            # 找到第一个"""开始
            start = source_code.find('"""')
            if start == -1:
                return None
            
            # 找到任务描述结束位置
            end = source_code.find('Here is a reference code to solve this task')
            if end == -1:
                # 如果没有找到reference code，找到第二个"""
                second_start = source_code.find('"""', start + 3)
                if second_start != -1:
                    end = second_start
                else:
                    return None
            
            description = source_code[start+3:end].strip()
            # 清理格式
            description = re.sub(r'^#\s*', '', description, flags=re.MULTILINE)
            return description
        
        return None
    except Exception as e:
        print(f"提取任务描述失败: {e}")
        return None

def load_bootcamp_dynamically(task_name: str):
    """动态加载bootcamp类"""
    try:
        # 构建模块路径
        module_path = f"internbootcamp.bootcamp.{task_name}.{task_name}"
        
        # 动态导入模块
        module = importlib.import_module(module_path)
        
        # 查找bootcamp类（通常是 TasknameBootcamp）
        class_name = f"{task_name.capitalize()}bootcamp"
        if hasattr(module, class_name):
            return getattr(module, class_name)
        
        # 尝试其他可能的类名格式
        for attr_name in dir(module):
            if attr_name.lower().endswith('bootcamp') and not attr_name.startswith('_'):
                return getattr(module, attr_name)
        
        print(f"未找到bootcamp类: {task_name}")
        return None
        
    except Exception as e:
        print(f"加载bootcamp失败 {task_name}: {e}")
        return None

def get_task_description_from_file(task_name: str) -> Optional[str]:
    """从文件中获取任务描述"""
    try:
        task_file = os.path.join(project_root, "internbootcamp", "bootcamp", task_name, f"{task_name}.py")
        if os.path.exists(task_file):
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return extract_task_description_from_source(content)
        return None
    except Exception as e:
        print(f"读取任务文件失败 {task_name}: {e}")
        return None

def fix_file_syntax(task_name: str) -> bool:
    """修复文件开头的注释语法问题"""
    try:
        task_file = os.path.join(project_root, "internbootcamp", "bootcamp", task_name, f"{task_name}.py")
        if not os.path.exists(task_file):
            return False
        
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要修复
        if content.startswith('"""#') or content.startswith('"#'):
            return True  # 已经是正确格式或不需要修复
            
        # 检查是否是损坏的格式（缺少开头的三引号）
        if content.startswith('#') and 'Here is a reference code to solve this task' in content:
            # 在开头添加三引号
            content = '"""' + content
            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"修复了文件语法: {task_name}")
            return True
        
        return True
    except Exception as e:
        print(f"修复文件语法失败 {task_name}: {e}")
        return False

def generate_test_cases(bootcamp_class, num_cases: int = 3) -> List[Dict]:
    """为给定的bootcamp生成测试用例"""
    test_cases = []
    
    try:
        # 创建bootcamp实例
        bootcamp = bootcamp_class()
        
        for i in range(num_cases):
            try:
                # 生成案例
                case = bootcamp.case_generator()
                prompt = bootcamp.prompt_func(case)
                
                test_cases.append({
                    "case": case,
                    "prompt": prompt
                })
                
            except Exception as e:
                print(f"  生成测试用例 {i+1} 失败: {e}")
                continue
                
    except Exception as e:
        print(f"创建bootcamp实例失败: {e}")
    
    return test_cases

def get_available_tasks() -> List[str]:
    """获取可用的任务列表"""
    bootcamp_dir = os.path.join(project_root, "internbootcamp", "bootcamp")
    if not os.path.exists(bootcamp_dir):
        return []
    
    tasks = []
    for item in os.listdir(bootcamp_dir):
        item_path = os.path.join(bootcamp_dir, item)
        if os.path.isdir(item_path):
            # 检查是否有对应的python文件
            py_file = os.path.join(item_path, f"{item}.py")
            if os.path.exists(py_file):
                tasks.append(item)
    
    return tasks

def select_representative_tasks(all_tasks: List[str], max_tasks: int = 5) -> List[str]:
    """选择代表性的任务"""
    import random
    
    # 优先选择一些经典任务
    priority_tasks = ['game24', 'sudoku', 'kakuro', 'minesweeper', 'maze']
    
    selected = []
    for task in priority_tasks:
        if task in all_tasks and len(selected) < max_tasks:
            selected.append(task)
    
    # 随机选择其他任务
    remaining = [t for t in all_tasks if t not in selected]
    random.shuffle(remaining)
    
    while len(selected) < max_tasks and remaining:
        selected.append(remaining.pop())
    
    return selected

def get_task_type(task_name: str) -> str:
    """根据任务名称推断任务类型"""
    type_mapping = {
        'game24': 'arithmetic_puzzle',
        'sudoku': 'logic_puzzle', 
        'kakuro': 'math_puzzle',
        'minesweeper': 'logic_puzzle',
        'maze': 'pathfinding',
        'nonograms': 'visual_puzzle',
        'slitherlink': 'logic_puzzle',
        'futoshiki': 'constraint_puzzle',
        'masyu': 'path_puzzle'
    }
    
    # 基于名称模式推断
    if 'puzzle' in task_name:
        return 'puzzle'
    elif 'cipher' in task_name or 'crypto' in task_name:
        return 'cryptography'
    elif 'kor_logic' in task_name:
        return 'logic_reasoning'
    elif 'kor_operation' in task_name:
        return 'operation_reasoning'
    elif task_name.startswith('c') or task_name.startswith('d'):
        return 'algorithm_problem'
    
    return type_mapping.get(task_name, 'unknown')

def generate_dataset():
    """生成包含多个任务的数据集"""
    print("开始生成多任务数据集...")
    
    # 获取可用任务
    all_tasks = get_available_tasks()
    print(f"发现 {len(all_tasks)} 个可用任务")
    
    # 选择代表性任务
    selected_tasks = select_representative_tasks(all_tasks, max_tasks=5)
    print(f"选择任务: {selected_tasks}")
    
    dataset = []
    task_id = 0
    
    for task_name in selected_tasks:
        print(f"\n处理任务: {task_name}")
        
        # 修复文件语法（如果需要）
        fix_file_syntax(task_name)
        
        # 获取任务描述
        task_description = get_task_description_from_file(task_name)
        if not task_description:
            print(f"  未能获取任务描述，跳过")
            continue
        
        # 动态加载bootcamp类
        bootcamp_class = load_bootcamp_dynamically(task_name)
        if not bootcamp_class:
            print(f"  未能加载bootcamp类，跳过")
            continue
        
        # 生成测试用例
        test_cases = generate_test_cases(bootcamp_class, num_cases=3)
        if not test_cases:
            print(f"  未能生成测试用例，跳过")
            continue
        
        print(f"  成功生成 {len(test_cases)} 个测试用例")
        
        dataset.append({
            "id": task_id,
            "task_name": task_name,
            "task_type": get_task_type(task_name),
            "task_description": task_description,
            "test_cases": test_cases
        })
        task_id += 1
    
    return dataset

def save_to_jsonl(data: List[Dict], filename: str):
    """保存数据到JSONL文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    """主函数"""
    print("=== 数据集处理脚本 (改进版) ===")
    
    # 生成数据集
    dataset = generate_dataset()
    
    if not dataset:
        print("未能生成任何数据集")
        return
    
    # 保存数据集
    output_file = "bootcamp_dataset.jsonl"
    save_to_jsonl(dataset, output_file)
    
    print(f"\n数据集生成完成！")
    print(f"- 总任务数: {len(dataset)}")
    print(f"- 总测试用例数: {sum(len(task['test_cases']) for task in dataset)}")
    print(f"- 输出文件: {output_file}")
    
    # 打印任务概要
    print("\n任务概要:")
    for task in dataset:
        print(f"- {task['task_name']} ({task['task_type']}): {len(task['test_cases'])} 个测试用例")

if __name__ == "__main__":
    main() 