## 2. HumanEvalHandler (handler.py)

from typing import List, Dict, Any
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
            raise ValueError(f"从HumanEval数据中提取问题时出错: {e}")

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
            'Counter': collections.Counter,
            'defaultdict': collections.defaultdict,
            'deque': collections.deque,
            'OrderedDict': collections.OrderedDict,
        }
        
        try:
            # 预处理代码，添加缺失的import
            code = self._preprocess_code_with_imports(code)
            
            print(f"[HumanEval]🚀: 生成的code是:\n{code}")
            
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
    
    def _extract_code_from_response(self, response: str) -> str:
        """
        从模型响应中提取Python代码。
        (从MbppHandler复用)
        """
        response = response.strip()
        
        if "```python" in response:
            parts = response.split("```python")
            if len(parts) > 1:
                code_part = parts[1].split("```")[0]
                return code_part.strip()
        elif "```" in response:
            parts = response.split("```")
            if len(parts) >= 2:
                code_part = parts[1]
                lines = code_part.split('\n')
                if lines and lines[0].strip().lower() in ['python', 'py']:
                    code_part = '\n'.join(lines[1:])
                return code_part.strip()
        
        if "def " in response:
            return response
        
        if "final answer:" in response.lower():
            parts = response.lower().split("final answer:")
            if len(parts) > 1:
                code = parts[-1].strip()
                return self._extract_code_from_response(code)
        
        return response
    
    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型生成的代码是否正确。
        通过运行HumanEval格式的测试用例来验证代码的正确性。
        
        :param model_output: 工作流执行后返回的代码
        :param ground_truth_data: 包含测试用例的完整数据
        :return: True 如果所有测试通过，否则为 False
        """
        try:
            # 提取生成的代码
            generated_code = self._extract_code_from_response(str(model_output))
            
            # 获取测试代码和函数名
            test_code = ground_truth_data.get('test', '')
            entry_point = ground_truth_data.get('entry_point', '')
            
            if not test_code or not entry_point:
                print("Warning: No test code or entry point found, falling back to LLM judge")
                return await self.llm_judge(model_output, ground_truth_data)
            
            # 执行代码并运行测试
            passed, message = self._execute_code_with_tests(
                generated_code, 
                test_code,
                entry_point
            )
            
            print(f"Code execution result: {message}")
            return passed
            
        except Exception as e:
            print(f"Error in HumanEval judge: {e}")
            return False