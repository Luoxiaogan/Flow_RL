## 2. HumanEvalHandler (handler.py)

from typing import List, Dict, Any
import typing
import re
import ast
import traceback
import asyncio
import sys
from io import StringIO
import contextlib

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class HumanevalHandler(BenchmarkHandler):
    """
    HumanEval 数据集的具体处理器。
    
    处理代码生成任务，需要生成Python函数并通过包装在check函数中的测试用例验证。
    """
    
    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
        """
        从 HumanEval 数据中提取函数签名和文档字符串，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **FUNCTION SIGNATURE AND SPECIFICATION:**
        [prompt with docstring]
        
        **ENTRY POINT:**
        Function name: [entry_point]
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取prompt（包含函数签名和docstring）和entry point
                prompt = problem.get('prompt', problem.get('question', ''))
                entry_point = problem.get('entry_point', '')
                answer = problem.get('answer', '')
                test = problem.get('test', '')

                # 组合问题
                formatted_problem = f"""---
**FUNCTION SIGNATURE AND SPECIFICATION:**
{prompt}

**ENTRY POINT:**
Function name: {entry_point}

**TEST CASES:(in the testing of the workflow, this will not be provided to the workflow)**
{test}

**REFERENCE ANSWER(code):(in the testing of the workflow, this will not be provided to the workflow)**
{answer}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从HumanEval数据中提取问题时出错: {e}")
        
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 HumanEval 数据中提取函数签名和文档字符串，并格式化为清晰的文本用于生成工作流。
        
        格式:
        ---
        **FUNCTION SIGNATURE AND SPECIFICATION:**
        [prompt with docstring]
        
        **ENTRY POINT:**
        Function name: [entry_point]
        ---
        
        (如果提供多个索引，则重复此结构)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取prompt（包含函数签名和docstring）和entry point
                prompt = problem.get('prompt', problem.get('question', ''))
                entry_point = problem.get('entry_point', '')

                # 组合问题
                formatted_problem = f"""---
**FUNCTION SIGNATURE AND SPECIFICATION:**
{prompt}

**ENTRY POINT:**
Function name: {entry_point}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"从HumanEval数据中, 提取问题时出错: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 HumanEval 问题的完整数据，用于后续的执行和验证。
        这包括prompt、测试用例、参考答案等信息。
        """
        return self._get_problem_by_index(index)
    
    def _execute_code_with_tests(self, code: str, test_code: str, entry_point: str) -> tuple[bool, str]:
        """
        安全地执行代码并运行HumanEval格式的测试用例。
        
        HumanEval的测试是一个check(candidate)函数，我们需要：
        1. 执行生成的代码定义函数
        2. 执行测试代码定义check函数
        3. 调用check函数，传入生成的函数
        
        返回: (是否全部通过, 错误信息)
        """
        # 创建执行环境
        import builtins
        
        # 预导入常用模块
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
        import typing
        
        exec_globals = {
            # 基础内建
            '__builtins__': builtins,

            # 常用标准库（整模块）
            'math'      : math,
            're'        : re,
            'collections': collections,
            'itertools' : itertools,
            'functools' : functools,
            'string'    : string,
            'datetime'  : datetime,
            'random'    : random,
            'heapq'     : heapq,
            'bisect'    : bisect,
            'copy'      : copy,
            'json'      : __import__('json'),
            'sys'       : __import__('sys'),

            # collections 高频类（裸写可用）
            'Counter'      : collections.Counter,
            'defaultdict'  : collections.defaultdict,
            'deque'        : collections.deque,
            'OrderedDict'  : collections.OrderedDict,
            'namedtuple'   : collections.namedtuple,
            'ChainMap'     : collections.ChainMap,

            # typing 裸写常用
            'List'       : typing.List,
            'Tuple'      : typing.Tuple,
            'Dict'       : typing.Dict,
            'Set'        : typing.Set,
            'FrozenSet'  : typing.FrozenSet,
            'Optional'   : typing.Optional,
            'Union'      : typing.Union,
            'Any'        : typing.Any,
            'Callable'   : typing.Callable,
            'Iterable'   : typing.Iterable,
            'Iterator'   : typing.Iterator,
            'Sequence'   : typing.Sequence,
            'Mapping'    : typing.Mapping,
        }
        
        try:
            # 预处理代码，添加缺失的import
            code = self._preprocess_code_with_imports(code)
            
            # print(f"[HumanEval]🚀: 生成的code是:\n{code}")
            
            # Step 1: 执行生成的函数代码
            exec(code, exec_globals)
            
            # Step 2: 确认函数已定义
            if entry_point not in exec_globals:
                return False, f"Function '{entry_point}' not found in generated code"
            
            # Step 3: 执行测试代码（定义check函数）
            exec(test_code, exec_globals)
            
            # Step 4: 调用check函数
            if 'check' not in exec_globals:
                return False, "Test function 'check' not found"
            
            try:
                # 捕获stdout和stderr
                with contextlib.redirect_stdout(StringIO()), contextlib.redirect_stderr(StringIO()):
                    # 调用check函数，传入生成的函数
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
    
    def _preprocess_code_with_imports(self, code: str) -> str:
        """
        预处理代码，自动添加可能缺失的import语句。
        (从MbppHandler复用)
        """
        import re
        
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

            # 适配两种数据格式
            # 1. 新格式：使用实际数据中的'test'字段
            test_code = ground_truth_data.get('test', '')
            
            # 2. 旧格式兼容：检查是否有test_list字段
            if not test_code:
                test_cases = ground_truth_data.get('test_list', [])
                test_setup = ground_truth_data.get('test_setup_code', '')
                if test_cases:
                    # 将旧格式转换为test_code
                    test_code = test_setup + '\n' + '\n'.join(test_cases)
            
            # 获取函数入口点
            entry_point = ground_truth_data.get('entry_point', '')
            
            if not test_code:
                # 如果没有测试代码，回退到LLM判断
                print("[Human_Eval] Warning: No test code found (neither 'test' nor 'test_list'), falling back to LLM judge")
                return await self.llm_judge(model_output, ground_truth_data)
            
            if not entry_point:
                # 尝试从prompt或question中提取函数名
                prompt = ground_truth_data.get('prompt', ground_truth_data.get('question', ''))
                import re
                match = re.search(r'def\s+(\w+)\s*\(', prompt)
                if match:
                    entry_point = match.group(1)
                else:
                    print("Warning: No entry_point found, falling back to LLM judge")
                    return await self.llm_judge(model_output, ground_truth_data)
            
            # 执行代码并运行测试
            passed, message = self._execute_code_with_tests(
                generated_code, 
                test_code,
                entry_point
            )
            
            # print(f"Code execution result: {message}")
            return passed
            
        except Exception as e:
            # print(f"Error in HumanEval judge: {e}")
            # 如果执行失败，认为答案错误
            return False