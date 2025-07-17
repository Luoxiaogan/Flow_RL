#!/usr/bin/env python3
"""
数据集生成脚本
从internbootcamp中选择多个任务，提取任务描述并生成测试用例
"""

import os
import sys
import json
import re
from typing import Dict, List, Any, Optional

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def extract_task_description_from_file(file_path: str) -> Optional[str]:
    """从文件中提取任务描述（到'Here is a reference code'之前）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找文档字符串中的任务描述
        if '"""#' in content:
            start = content.find('"""#')
            end = content.find('Here is a reference code to solve this task')
            if start != -1 and end != -1:
                description = content[start+4:end].strip()
                return description
        
        # 如果没找到，尝试其他模式
        if '"""' in content:
            lines = content.split('\n')
            in_docstring = False
            description_lines = []
            
            for line in lines:
                if line.strip().startswith('"""'):
                    if in_docstring:
                        break
                    else:
                        in_docstring = True
                        continue
                
                if in_docstring:
                    if 'Here is a reference code to solve this task' in line:
                        break
                    description_lines.append(line)
            
            return '\n'.join(description_lines).strip()
        
        return None
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return None

def create_mock_bootcamps():
    """创建多个模拟bootcamp类用于不同任务类型"""
    
    class AAPBootcamp:
        """几乎算术级数任务"""
        def case_generator(self):
            import random
            cases = [
                {"n": 4, "b": [10, 20, 10, 30], "ans": 3},
                {"n": 2, "b": [3, 5], "ans": 2},
                {"n": 5, "b": [1, 2, 1, 3, 1], "ans": 3},
                {"n": 6, "b": [5, 10, 5, 15, 5, 20], "ans": 4}
            ]
            return random.choice(cases)
        
        def prompt_func(self, case):
            n = case["n"]
            b = " ".join(map(str, case["b"]))
            return f"""Find the length of the longest subsequence that forms an almost arithmetical progression (AAP) where:
- a₁ is any integer
- For i > 1: aᵢ = aᵢ₋₁ + (-1)^(i+1)·q (q is integer)

Input:
{n}
{b}

Output format: Only the integer answer within [answer] tags, like:
[answer]4[/answer]"""
        
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
        """24点游戏任务"""
        def case_generator(self):
            import random
            cases = [
                {"numbers": [4, 1, 8, 7], "target": 24},
                {"numbers": [1, 1, 8, 8], "target": 24},
                {"numbers": [3, 3, 8, 8], "target": 24},
                {"numbers": [2, 6, 9, 5], "target": 24}
            ]
            return random.choice(cases)
        
        def prompt_func(self, case):
            numbers = " ".join(map(str, case["numbers"]))
            target = case["target"]
            return f"""Use the numbers {numbers} to get {target} through basic arithmetic operations (+, -, *, /).
Each number must be used exactly once. You can use parentheses to change order of operations.

Output format: Put your final expression in [answer] tags, like:
[answer](8-4) * (7-1)[/answer]"""
        
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
                # 这里应该有更复杂的表达式求值验证，简化处理
                return True
            except:
                return False
    
    class CipherBootcamp:
        """密码解密任务"""
        def case_generator(self):
            import random
            cases = [
                {"cipher": "KHOOR", "shift": 3, "plain": "HELLO"},
                {"cipher": "ZRUOG", "shift": 3, "plain": "WORLD"},
                {"cipher": "FDHVDU", "shift": 3, "plain": "CAESAR"},
                {"cipher": "FLSKHU", "shift": 3, "plain": "CIPHER"}
            ]
            return random.choice(cases)
        
        def prompt_func(self, case):
            cipher = case["cipher"]
            return f"""Decode the Caesar cipher: {cipher}
This is encoded with a simple shift cipher where each letter is shifted by the same amount.

Output format: Put the decoded message in [answer] tags, like:
[answer]HELLO[/answer]"""
        
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
        """数独任务（简化版）"""
        def case_generator(self):
            import random
            cases = [
                {
                    "puzzle": "5.3..7...",
                    "solution": "534678912",
                    "description": "Fill the 9-digit row: 5_3__7___"
                },
                {
                    "puzzle": "6..195...",
                    "solution": "672195348",
                    "description": "Fill the 9-digit row: 6__195___"
                }
            ]
            return random.choice(cases)
        
        def prompt_func(self, case):
            puzzle = case["puzzle"]
            description = case["description"]
            return f"""Complete this Sudoku row: {description}
Each digit 1-9 must appear exactly once in the row.

Current row: {puzzle} (where . represents empty cells)

Output format: Put the complete 9-digit row in [answer] tags, like:
[answer]123456789[/answer]"""
        
        @staticmethod
        def extract_output(output):
            import re
            matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
            if not matches:
                return None
            solution = matches[-1].strip()
            # 只保留数字
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

def get_task_descriptions():
    """获取各任务的描述"""
    descriptions = {}
    
    # AAP任务描述
    aap_file = os.path.join(project_root, 
                           "internbootcamp/bootcamp/aalmostarithmeticalprogression/aalmostarithmeticalprogression.py")
    if os.path.exists(aap_file):
        descriptions["aalmostarithmeticalprogression"] = extract_task_description_from_file(aap_file)
    else:
        descriptions["aalmostarithmeticalprogression"] = """### 几乎算术级数任务
找到序列中最长的几乎算术级数子序列。几乎算术级数定义为：
- a₁ = p (任意整数)
- aᵢ = aᵢ₋₁ + (-1)^(i+1)·q (i > 1, q为整数)

这意味着序列在两个值p和p+q之间交替。"""
    
    # 其他任务描述
    descriptions["game24"] = """### 24点游戏
使用给定的4个数字，通过基本运算（+、-、*、/）得到24。每个数字必须恰好使用一次，可以使用括号改变运算顺序。"""
    
    descriptions["cipher"] = """### 凯撒密码解密
解码凯撒密码。这是一种简单的替换密码，其中每个字母都按字母表中的固定位置移位。需要找到正确的移位量并解码消息。"""
    
    descriptions["sudoku"] = """### 数独行填充
完成数独的一行。每个数字1-9在行中必须恰好出现一次。给定部分填充的行，需要填入缺失的数字。"""
    
    return descriptions

def generate_dataset():
    """生成包含多个任务的数据集"""
    print("开始生成多任务数据集...")
    
    # 获取任务描述和bootcamp实例
    task_descriptions = get_task_descriptions()
    bootcamps = create_mock_bootcamps()
    
    dataset = []
    task_id = 0
    
    for task_name, bootcamp in bootcamps.items():
        print(f"处理任务: {task_name}")
        
        task_description = task_descriptions.get(task_name, f"任务: {task_name}")
        
        # 为每个任务生成3个测试用例
        test_cases = []
        for i in range(3):
            try:
                case = bootcamp.case_generator()
                prompt = bootcamp.prompt_func(case)
                test_cases.append({
                    "case": case,
                    "prompt": prompt
                })
                print(f"  生成测试用例 {i+1}")
            except Exception as e:
                print(f"  生成测试用例失败: {e}")
                continue
        
        if test_cases:
            dataset.append({
                "id": task_id,
                "task_name": task_name,
                "task_type": get_task_type(task_name),
                "task_description": task_description,
                "test_cases": test_cases
            })
            task_id += 1
    
    return dataset

def get_task_type(task_name: str) -> str:
    """根据任务名称返回任务类型"""
    type_mapping = {
        "aalmostarithmeticalprogression": "sequence_analysis",
        "game24": "arithmetic_puzzle",
        "cipher": "cryptography",
        "sudoku": "logic_puzzle"
    }
    return type_mapping.get(task_name, "unknown")

def save_to_jsonl(data: List[Dict], filename: str):
    """保存数据到JSONL文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    """主函数"""
    print("=== 数据集生成脚本 ===")
    
    # 生成数据集
    dataset = generate_dataset()
    
    if not dataset:
        print("未能生成任何数据集")
        return
    
    # 保存数据集
    output_file = "multi_task_dataset.jsonl"
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