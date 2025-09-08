## HumanevalplusHandler (handler.py)

from typing import List, Dict, Any
import ast
import traceback
import sys
import re
from io import StringIO
import contextlib
import random

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class HumanevalplusHandler(BenchmarkHandler):
    """
    HumanEval+ dataset handler.
    
    处理增强版代码生成任务，包含比原始HumanEval多80倍的测试用例。
    """
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从HumanEval+数据中提取函数签名和规范，格式化为清晰的文本。
        
        关键理解：测试用例嵌入在test字段的check函数中，
        我们需要解析这个函数来提取示例测试。
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # print("\n\n. problem:\n\n", problem)
                # 提取核心组件
                prompt = problem.get('prompt', '')
                # print(f"\n\n🤡 🤡 🤡 🤡 🤡 🤡 prompt: {prompt}...")  # 调试输出
                entry_point = problem.get('entry_point', '')
                # print(f"🤡 🤡 🤡 🤡 🤡 🤡 entry_point: {entry_point}")  # 调试输出
                canonical_solution = problem.get('canonical_solution', '')
                # print(f"🤡 🤡 🤡 🤡 🤡 🤡 canonical_solution: {canonical_solution}...")  # 调试输出
                test_code = problem.get('test', '')
                # print(f"\n\n🤡 🤡 🤡 🤡 🤡 🤡 test_code: {test_code[:1000]}...")  # 调试输出
                
                # 从test代码中提取示例测试用例
                test_examples = self._extract_test_examples_from_code(test_code)
                # print(f"\n\n🤡 🤡 🤡 🤡 🤡 🤡 test_examples: {test_examples}...")  # 调试输出
                
                # 构建格式化的问题
                formatted_problem = f"""---
**FUNCTION SIGNATURE AND SPECIFICATION:**
{prompt}

**ENTRY POINT:**
Function name: {entry_point}

**SAMPLE TEST CASES (3 random examples from extensive test suite):**
```python
{test_examples}
```

**CANONICAL SOLUTION (Reference - Study approach but DO NOT COPY):**
```python
{canonical_solution}
```

**NOTE**: The actual evaluation uses 80x more test cases including edge cases.
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except Exception as e:
            raise ValueError(f"Error extracting problem from HumanEval+ data: {e}")

    def _extract_test_examples_from_code(self, test_code: str) -> str:
        """
        从test代码中解析出inputs和results列表，然后随机选择3个测试用例。
        
        HumanEval+的test字段包含形如：
        def check(candidate):
            inputs = [[...], [...], ...]
            results = [...]
            for i, (inp, exp) in enumerate(zip(inputs, results)):
                assertion(candidate(*inp), exp, 0)
        """
        try:
            # 使用正则表达式找到inputs和results的定义
            inputs_match = re.search(r'inputs\s*=\s*(\[.*?\])\s*results', test_code, re.DOTALL)
            results_match = re.search(r'results\s*=\s*(\[.*?\])\s*for', test_code, re.DOTALL)
            
            if inputs_match and results_match:
                # 安全地评估列表
                inputs_str = inputs_match.group(1)
                results_str = results_match.group(1)
                
                # 使用ast.literal_eval安全地解析Python列表
                inputs = ast.literal_eval(inputs_str)
                results = ast.literal_eval(results_str)
                
                # 随机选择最多3个测试用例
                num_tests = min(3, len(inputs))
                if num_tests > 0:
                    selected_indices = random.sample(range(len(inputs)), num_tests)
                    
                    examples = []
                    for idx in selected_indices:
                        inp = inputs[idx]
                        exp = results[idx]
                        # 格式化为assert语句
                        examples.append(f"assert candidate{inp} == {exp}")
                    
                    return '\n'.join(examples)
            
            # 如果解析失败，返回通用说明
            return "# Test cases verify correctness across various inputs"
            
        except Exception as e:
            # 如果出错，返回简单说明
            return f"# Test cases available but not shown (parsing error: {e})"

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个HumanEval+问题的完整数据用于执行和验证。
        """
        data = self._get_problem_by_index(index)
        
        # 调试信息
        print(f"[DEBUG] Loading problem at index {index}")
        print(f"[DEBUG] task_id: {data.get('task_id', 'NOT FOUND')}")
        print(f"[DEBUG] entry_point: {data.get('entry_point', 'NOT FOUND')}")
        print(f"[DEBUG] Has test: {'test' in data and bool(data['test'])}")
        
        return data
    
    def _preprocess_code_with_imports(self, code: str) -> str:
        """
        预处理代码，自动添加可能缺失的import语句。
        """
        module_patterns = {
            'math': ['sqrt', 'ceil', 'floor', 'pow', 'exp', 'log', 'sin', 'cos', 'tan', 'pi', 'e', 'gcd', 'factorial'],
            're': ['match', 'search', 'findall', 'sub', 'compile', 'split'],
            'collections': ['Counter', 'defaultdict', 'deque', 'OrderedDict', 'namedtuple'],
            'itertools': ['chain', 'combinations', 'permutations', 'product', 'cycle', 'repeat', 'groupby'],
            'functools': ['reduce', 'partial', 'lru_cache', 'wraps'],
            'datetime': ['datetime', 'date', 'time', 'timedelta'],
            'random': ['random', 'randint', 'choice', 'shuffle', 'sample', 'uniform'],
            'heapq': ['heappush', 'heappop', 'heapify', 'heappushpop', 'nlargest', 'nsmallest'],
            'bisect': ['bisect_left', 'bisect_right', 'insort_left', 'insort_right'],
        }
        
        imported_modules = set()
        for line in code.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                if 'import ' in line:
                    parts = line.replace('from ', '').replace('import ', '').split()
                    if parts:
                        imported_modules.add(parts[0].split('.')[0])
        
        needed_imports = []
        for module, attributes in module_patterns.items():
            if module in imported_modules:
                continue
            
            for attr in attributes:
                if re.search(rf'\b{module}\.{attr}\b', code):
                    needed_imports.append(f'import {module}')
                    break
                if re.search(rf'\b{attr}\s*\(', code) and module not in imported_modules:
                    if module == 'collections' and attr in ['Counter', 'defaultdict', 'deque']:
                        needed_imports.append(f'from {module} import {attr}')
                    elif module == 'itertools' and attr in ['chain', 'combinations', 'permutations', 'product']:
                        needed_imports.append(f'from {module} import {attr}')
                    elif module == 'functools' and attr == 'reduce':
                        needed_imports.append(f'from {module} import {attr}')
        
        if needed_imports:
            needed_imports = list(dict.fromkeys(needed_imports))
            return '\n'.join(needed_imports) + '\n\n' + code
        
        return code
    
    def _validate_and_fix_indentation(self, code: str) -> str:
        """
        验证并修复代码缩进问题。
        """
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 将tab转换为4个空格
            fixed_line = line.replace('\t', '    ')
            fixed_lines.append(fixed_line)
        
        fixed_code = '\n'.join(fixed_lines)
        
        # 验证语法
        try:
            ast.parse(fixed_code)
            return fixed_code
        except SyntaxError as e:
            print(f"Warning: Code has syntax errors after indentation fix: {e}")
            return code
    
    def _extract_code_from_response(self, response: str) -> str:
        """
        从模型响应中提取Python代码，处理各种可能的格式。
        
        特别处理solve()包装器的问题。
        """
        response = response.rstrip('\n')
        
        # 方法1：提取markdown代码块
        python_block_pattern = r'```python\s*\n(.*?)```'
        matches = re.findall(python_block_pattern, response, re.DOTALL)
        if matches:
            code = matches[0]
            
            # 检查并处理solve()包装器
            if 'def solve():' in code:
                # 提取solve函数内部定义的实际函数
                lines = code.split('\n')
                actual_func_lines = []
                in_actual_func = False
                indent_level = 0
                
                for line in lines:
                    # 跳过solve()定义和最外层的return
                    if line.strip().startswith('def solve():'):
                        continue
                    
                    # 找到内部函数定义
                    if re.match(r'^\s+def\s+\w+', line):
                        in_actual_func = True
                        # 计算需要去除的缩进
                        indent_level = len(line) - len(line.lstrip())
                        # 去除solve函数的缩进
                        actual_func_lines.append(line.lstrip())
                    elif in_actual_func:
                        # 如果是return语句且在solve函数级别，跳过
                        if line.strip().startswith('return') and len(line) - len(line.lstrip()) <= 4:
                            continue
                        # 否则去除solve的缩进级别
                        if line.strip():
                            # 移除solve的缩进（通常是4个空格）
                            deindented = line[4:] if line.startswith('    ') else line
                            actual_func_lines.append(deindented)
                        else:
                            actual_func_lines.append(line)
                
                if actual_func_lines:
                    code = '\n'.join(actual_func_lines)
            
            while code.endswith('\n\n'):
                code = code[:-1]
            return code
        
        # 方法2：通用代码块
        generic_block_pattern = r'```\s*\n(.*?)```'
        matches = re.findall(generic_block_pattern, response, re.DOTALL)
        if matches:
            code = matches[0]
            # 处理可能的语言标识符
            lines = code.split('\n')
            if lines and lines[0].strip().lower() in ['python', 'py']:
                code = '\n'.join(lines[1:])
            while code.endswith('\n\n'):
                code = code[:-1]
            return code
        
        # 方法3：查找函数定义
        if re.search(r'^\s*def\s+\w+\s*\(', response, re.MULTILINE):
            lines = response.split('\n')
            start_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or \
                   line.strip().startswith('from ') or \
                   line.strip().startswith('def '):
                    start_idx = i
                    break
            
            code = '\n'.join(lines[start_idx:])
            while code.endswith('\n\n'):
                code = code[:-1]
            return code
        
        # 最后的备选
        return response
    
    def _execute_code_with_tests(self, code: str, test_code: str, entry_point: str) -> tuple[bool, str]:
        """
        安全地执行代码并运行HumanEval+格式的测试用例。
        """
        # 创建执行环境
        import builtins
        import math
        import collections
        import itertools
        import functools
        import string
        import datetime
        import random
        import heapq
        import bisect
        import copy
        import numpy as np
        from typing import List, Dict, Tuple, Any, Optional
        
        exec_globals = {
            '__builtins__': builtins,
            'math': math,
            're': re,
            'collections': collections,
            'itertools': itertools,
            'functools': functools,
            'string': string,
            'datetime': datetime,
            'random': random,
            'heapq': heapq,
            'bisect': bisect,
            'copy': copy,
            'np': np,
            'numpy': np,
            'Counter': collections.Counter,
            'defaultdict': collections.defaultdict,
            'deque': collections.deque,
            'OrderedDict': collections.OrderedDict,
            'List': List,
            'Dict': Dict,
            'Tuple': Tuple,
            'Any': Any,
            'Optional': Optional,
        }
        
        try:
            # 预处理代码
            code = self._preprocess_code_with_imports(code)
            
            print(f"[HumanEval+] Executing code:\n{code[:200]}...")
            
            # 执行生成的代码
            exec(code, exec_globals)
            
            # 确认函数已定义
            if entry_point not in exec_globals:
                return False, f"Function '{entry_point}' not found in generated code"
            
            # 执行测试代码
            exec(test_code, exec_globals)
            
            # 确认check函数存在
            if 'check' not in exec_globals:
                return False, "Test function 'check' not found"
            
            try:
                # 捕获输出
                with contextlib.redirect_stdout(StringIO()), contextlib.redirect_stderr(StringIO()):
                    # 调用check函数
                    exec_globals['check'](exec_globals[entry_point])
                return True, "All tests passed!"
            except AssertionError as e:
                return False, f"Test failed: {str(e)}"
            except Exception as e:
                return False, f"Test execution error: {str(e)}"
                
        except SyntaxError as e:
            return False, f"Syntax error in code: {str(e)}"
        except Exception as e:
            return False, f"Execution error: {str(e)}\n{traceback.format_exc()}"
    
    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型输出是否正确解决HumanEval+问题。
        """
        if not model_output or not ground_truth_data:
            print("[HumanEval+] Missing model output or ground truth data")
            return False
        
        # 提取代码
        generated_code = self._extract_code_from_response(str(model_output))
        generated_code = self._validate_and_fix_indentation(generated_code)
        
        # 获取测试组件
        entry_point = ground_truth_data.get('entry_point', '')
        test_code = ground_truth_data.get('test', '')
        
        if not entry_point:
            print(f"[HumanEval+] Missing entry_point in ground truth data")
            return False
        
        if not test_code:
            print(f"[HumanEval+] Missing test code in ground truth data")
            return False
        
        # 执行验证
        passed, error_msg = self._execute_code_with_tests(generated_code, test_code, entry_point)
        
        if not passed:
            print(f"[HumanEval+] Tests failed: {error_msg[:300]}...")
            
        return passed