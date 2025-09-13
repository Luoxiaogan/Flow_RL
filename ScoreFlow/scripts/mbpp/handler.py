## 2. MbppHandler (handler.py)
# ScoreFlow/scripts/mbpp/handler.py

from typing import List, Dict, Any
import re
import ast
import traceback
import asyncio
import sys
from io import StringIO
import contextlib

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class MbppHandler(BenchmarkHandler):
    """
    MBPP (Mostly Basic Python Problems) 数据集的具体处理器。
    
    处理代码生成任务，需要生成Python函数并通过测试用例验证。
    """
    
    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
        """
        从 MBPP 数据中提取编程任务描述，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **TASK:**
        [task description]
        
        **TEST CASES:**
        [test case 1]
        [test case 2]
        ...
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取任务描述和测试用例
                task_description = problem.get('text', problem.get('question', ''))
                test_cases = problem.get('test_list', [])
                answer = problem.get('answer', '')

                # 格式化测试用例
                test_cases_text = "**TEST CASES:**\n"
                if test_cases:
                    for test_case in test_cases:
                        test_cases_text += f"{test_case}\n"
                else:
                    test_cases_text += "No test cases provided.\n"
                
                # 组合任务描述和测试用例
                formatted_problem = f"""---
**TASK:**
{task_description}

**TEST CASES:(for you to know the function name and expected input types, testing of the workflow, this WILL be provided to the workflow, since it is essential for understanding the function name)**
{test_cases_text.strip()}

**REFERENCE ANSWER(code):(in the testing of the workflow, this will not be provided to the workflow)**
{answer}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从MBPP数据中提取问题时出错: {e}")

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 MBPP 数据中提取编程任务描述，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **TASK:**
        [task description]
        
        **TEST CASES:**
        [test case 1]
        [test case 2]
        ...
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取任务描述和测试用例
                task_description = problem.get('text', problem.get('question', ''))
                test_cases = problem.get('test_list', [])
                answer = problem.get('answer', '')

                # 格式化测试用例
                test_cases_text = "**TEST CASES:**\n"
                if test_cases:
                    for test_case in test_cases:
                        test_cases_text += f"{test_case}\n"
                else:
                    test_cases_text += "No test cases provided.\n"
                
                # 组合任务描述和测试用例
                formatted_problem = f"""---
**TASK:**
{task_description}

**TEST CASES:(for you to know the function name and expected input types, testing of the workflow, this WILL be provided to the workflow, since it is essential for understanding the function name)**
{test_cases_text.strip()}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从MBPP数据中提取问题时出错: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 MBPP 问题的完整数据，用于后续的执行和验证。
        这包括任务描述、测试用例、参考答案等信息。
        """
        return self._get_problem_by_index(index)
    
    def _execute_code_with_tests(self, code: str, test_cases: List[str], test_setup: str = "") -> tuple[bool, str]:
        """
        安全地执行代码并运行测试用例。
        
        返回: (是否全部通过, 错误信息)
        """
        # 创建一个执行环境，包含必要的内置函数
        # 注意：assert 是关键字，会在 exec 中自动可用，不需要也不能显式传递
        import builtins
        
        # 预导入常用的标准库模块，以防生成的代码忘记import
        # 这些是MBPP中常用的模块
        import math
        import re
        import collections
        import itertools
        import functools
        import string
        import datetime
        import random
        import heapq
        import bisect
        import copy
        
        exec_globals = {
            '__builtins__': builtins,
            # 预先提供常用模块，以防代码忘记import
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
            # 也支持from X import Y的常用情况
            'Counter': collections.Counter,
            'defaultdict': collections.defaultdict,
            'deque': collections.deque,
            'OrderedDict': collections.OrderedDict,
            'chain': itertools.chain,
            'combinations': itertools.combinations,
            'permutations': itertools.permutations,
            'product': itertools.product,
            'reduce': functools.reduce,
        }
        
        try:
            # 预处理代码，自动添加可能缺失的import
            code = self._preprocess_code_with_imports(code)

            print(f"[MBPP]🚀: 生成的code是:\n{code}")
            
            # 首先执行测试前置代码（如果有）
            if test_setup:
                exec(test_setup, exec_globals)
            
            # 执行生成的代码
            exec(code, exec_globals)
            
            # 运行每个测试用例
            passed_tests = 0
            failed_tests = []
            
            for i, test_case in enumerate(test_cases):
                print(f"[MBPP]🚀: 测试用例:\n{test_case}")
                try:
                    # 捕获stdout用于调试
                    with contextlib.redirect_stdout(StringIO()):
                        exec(test_case, exec_globals)
                    passed_tests += 1
                except AssertionError as e:
                    failed_tests.append(f"Test {i+1} failed: {test_case}")
                    print(f"[MBPP]🚀: 测试用例失败:\n{test_case}")
                except Exception as e:
                    failed_tests.append(f"Test {i+1} error: {test_case} - {str(e)}")
                    print(f"[MBPP]🚀: 测试用例错误:\n{test_case} - {str(e)}")

            if failed_tests:
                return False, f"Passed {passed_tests}/{len(test_cases)} tests. Failed: {'; '.join(failed_tests)}"
            else:
                return True, f"All {passed_tests} tests passed!"
                
        except SyntaxError as e:
            return False, f"Syntax error in code: {str(e)}"
        except Exception as e:
            return False, f"Execution error: {str(e)}\n{traceback.format_exc()}"
    
    def _preprocess_code_with_imports(self, code: str) -> str:
        """
        预处理代码，自动添加可能缺失的import语句。
        通过分析代码中使用的模块，智能添加必要的import。
        """
        import re
        
        # 需要检查的标准库模块及其常用属性
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
        
        # 检查代码中是否已经import了这些模块
        imported_modules = set()
        import_lines = []
        
        # 查找已有的import语句
        for line in code.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_lines.append(line)
                # 提取模块名
                if 'import ' in line:
                    parts = line.replace('from ', '').replace('import ', '').split()
                    if parts:
                        imported_modules.add(parts[0].split('.')[0])
        
        # 检查代码中使用了哪些模块
        needed_imports = []
        for module, attributes in module_patterns.items():
            if module in imported_modules:
                continue  # 已经导入了
            
            # 检查是否使用了该模块的属性
            for attr in attributes:
                # 检查 module.attr 的使用
                if re.search(rf'\b{module}\.{attr}\b', code):
                    needed_imports.append(f'import {module}')
                    break
                # 检查直接使用的函数（可能需要from ... import）
                if re.search(rf'\b{attr}\s*\(', code) and module not in imported_modules:
                    # 检查是否是该模块特有的函数
                    if module == 'collections' and attr in ['Counter', 'defaultdict', 'deque']:
                        needed_imports.append(f'from {module} import {attr}')
                    elif module == 'itertools' and attr in ['chain', 'combinations', 'permutations', 'product']:
                        needed_imports.append(f'from {module} import {attr}')
                    elif module == 'functools' and attr == 'reduce':
                        needed_imports.append(f'from {module} import {attr}')
        
        # 如果需要添加import，将它们加到代码开头
        if needed_imports:
            # 去重
            needed_imports = list(dict.fromkeys(needed_imports))
            return '\n'.join(needed_imports) + '\n\n' + code
        
        return code
    
    def _validate_and_fix_indentation(self, code: str) -> str:
        """
        验证并修复代码缩进问题。
        
        这个方法检查代码的缩进是否一致，
        如果发现混合使用tab和空格，会统一转换为4个空格。
        """
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 将tab转换为4个空格
            fixed_line = line.replace('\t', '    ')
            fixed_lines.append(fixed_line)
        
        # 重新组合代码
        fixed_code = '\n'.join(fixed_lines)
        
        # 验证语法
        try:
            ast.parse(fixed_code)
            return fixed_code
        except SyntaxError as e:
            # 如果还有语法错误，返回原始代码并记录警告
            print(f"Warning: Code has syntax errors after indentation fix: {e}")
            return code
    
    def _extract_code_from_response(self, response: str) -> str:
        """
        从模型响应中提取Python代码。
        
        提取优先级：
        1. ```python 代码块（markdown格式）
        2. ``` 通用代码块
        3. 包含 def 的原始代码
        4. Final Answer 后的内容
        5. 原始响应
        
        注意：保持代码缩进的完整性
        """
        # 不使用strip()来避免破坏缩进，只移除末尾的换行
        response = response.rstrip('\n')
        
        # 方法1：提取markdown python代码块
        # 同时处理 ```python 和 ```python\n 的情况
        python_block_pattern = r'```python\s*\n(.*?)```'
        matches = re.findall(python_block_pattern, response, re.DOTALL)
        if matches:
            # 返回第一个匹配的代码块
            # 注意：不使用strip()，保留缩进
            code = matches[0]
            # 只移除末尾多余的空行
            while code.endswith('\n\n'):
                code = code[:-1]
            return code
        
        # 方法2：提取通用markdown代码块
        generic_block_pattern = r'```\s*\n(.*?)```'
        matches = re.findall(generic_block_pattern, response, re.DOTALL)
        if matches:
            code = matches[0]
            # 检查是否第一行是语言标识符
            lines = code.split('\n')
            if lines and lines[0].strip().lower() in ['python', 'py']:
                # 移除语言标识符行，但保留其他行的缩进
                code = '\n'.join(lines[1:])
            # 只移除末尾多余的空行
            while code.endswith('\n\n'):
                code = code[:-1]
            return code
        
        # 方法3：查找Final Answer标记
        if "final answer:" in response.lower():
            # 找到最后一个Final Answer
            parts = response.split("Final Answer:")
            if len(parts) == 1:
                # 尝试小写分割
                parts = response.split("final answer:")
            
            if len(parts) > 1:
                potential_code = parts[-1]
                # 递归调用以处理Final Answer后可能的代码块
                extracted = self._extract_code_from_response(potential_code)
                if extracted != potential_code:  # 如果成功提取了代码块
                    return extracted
                # 否则清理并返回Final Answer后的内容
                return potential_code.lstrip()
        
        # 方法4：检查是否包含函数定义
        if re.search(r'^\s*def\s+\w+\s*\(', response, re.MULTILINE):
            # 看起来像Python代码，找到第一个import或def开始的位置
            lines = response.split('\n')
            start_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or \
                line.strip().startswith('from ') or \
                line.strip().startswith('def '):
                    start_idx = i
                    break
            
            # 返回从第一个代码行开始的内容
            code = '\n'.join(lines[start_idx:])
            # 只移除末尾多余的空行
            while code.endswith('\n\n'):
                code = code[:-1]
            return code
        
        # 方法5：返回原始响应（最后的备选）
        return response

    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型生成的代码是否正确。
        通过运行测试用例来验证代码的正确性。
        
        :param model_output: 工作流执行后返回的代码
        :param ground_truth_data: 包含测试用例的完整数据
        :return: True 如果所有测试通过，否则为 False
        """
        try:
            # 提取代码
            generated_code = self._extract_code_from_response(str(model_output))

            generated_code = self._validate_and_fix_indentation(generated_code)

            # 获取测试用例
            test_cases = ground_truth_data.get('test_list', [])
            test_setup = ground_truth_data.get('test_setup_code', '')
            
            if not test_cases:
                # 如果没有测试用例，回退到LLM判断
                print("[MBPP] Warning: No test cases found, falling back to LLM judge")
                return await self.llm_judge(model_output, ground_truth_data)
            
            # 执行代码并运行测试
            passed, message = self._execute_code_with_tests(
                generated_code, 
                test_cases, 
                test_setup
            )
            
            print(f"Code execution result: {message}")
            return passed
            
        except Exception as e:
            print(f"Error in MBPP judge: {e}")
            # 如果执行失败，认为答案错误
            return False