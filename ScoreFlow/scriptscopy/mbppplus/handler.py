# ScoreFlow/scripts/mbppplus/handler.py

from typing import List, Dict, Any
import ast
import traceback
import re
import sys
from io import StringIO
import contextlib

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class MbppplusHandler(BenchmarkHandler):
    """
    MBPP+ (Enhanced Mostly Basic Python Problems) dataset handler.
    
    处理增强版的基础Python编程问题，包含比原始MBPP更全面的测试套件。
    每个问题包括基础测试用例和扩展测试，用于验证解决方案的正确性和鲁棒性。
    """
    
    def get_prompt_text_workflow_generation(self, indices: List[int]) -> str:
        """
        从MBPP+数据中提取编程任务描述，格式化为清晰的工作流生成文本。
        
        关键处理：
        - 从prompt字段提取任务描述
        - 从code字段提取函数签名和参考实现
        - 从test_list提取基础测试用例
        - 提供清晰的格式化输出
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取核心组件
                task_description = problem.get('prompt', '')
                # print(f"😈 😈 😈 😈 😈 task_description={task_description}")
                reference_code = problem.get('code', '')
                # print(f"😈 😈 😈 😈 😈 reference_code={reference_code}")
                test_cases = problem.get('test_list', [])
                
                # 从参考代码中提取函数签名
                function_signature = self._extract_function_signature(reference_code)
                # print(f"😈 😈 😈 😈 😈 function_signature={function_signature}")
                
                # 格式化基础测试用例
                test_cases_text = ""
                if test_cases:
                    for i, test in enumerate(test_cases[:5], 1):  # 显示前5个测试用例
                        test_cases_text += f"{test}\n"
                else:
                    test_cases_text = "# No basic test cases provided\n"
                # print(f"😈 😈 😈 😈 😈 test_cases_text={test_cases_text}")
                
                # 构建格式化的问题
                formatted_problem = f"""---
**TASK DESCRIPTION:**
{task_description}

**FUNCTION SIGNATURE:**
```python
{function_signature}
```

**BASIC TEST CASES:**
```python
{test_cases_text.strip()}
```

**REFERENCE SOLUTION:**
```python
{reference_code.strip()}
```

**NOTE:** The actual evaluation includes extensive additional test cases beyond those shown.
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
            
        except Exception as e:
            raise ValueError(f"Error extracting problem from MBPP+ data: {e}")
        
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从MBPP+数据中提取编程任务描述，格式化为清晰的工作流生成文本。
        
        关键处理：
        - 从prompt字段提取任务描述
        - 从code字段提取函数签名和参考实现
        - 从test_list提取基础测试用例
        - 提供清晰的格式化输出
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # 提取核心组件
                task_description = problem.get('prompt', '')
                # print(f"😈 😈 😈 😈 😈 task_description={task_description}")
                reference_code = problem.get('code', '')
                # print(f"😈 😈 😈 😈 😈 reference_code={reference_code}")
                test_cases = problem.get('test_list', [])
                
                # 从参考代码中提取函数签名
                function_signature = self._extract_function_signature(reference_code)
                # print(f"😈 😈 😈 😈 😈 function_signature={function_signature}")
                
                # 格式化基础测试用例
                test_cases_text = ""
                if test_cases:
                    for i, test in enumerate(test_cases[:5], 1):  # 显示前5个测试用例
                        test_cases_text += f"{test}\n"
                else:
                    test_cases_text = "# No basic test cases provided\n"
                # print(f"😈 😈 😈 😈 😈 test_cases_text={test_cases_text}")
                
                # 构建格式化的问题
                formatted_problem = f"""---
**TASK DESCRIPTION:**
{task_description}

**FUNCTION SIGNATURE:**
```python
{function_signature}
```
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
            
        except Exception as e:
            raise ValueError(f"Error extracting problem from MBPP+ data: {e}")
    def get_prompt_text_example(self, indices: List[int]) -> str:
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
                
                # 格式化测试用例
                test_cases_text = "**TEST CASES(FOR YOU TO KNOW THE FUNCTION NAME):**\n"
                i=0
                if test_cases:
                    for test_case in test_cases:
                        if i<=2:
                            test_cases_text += f"{test_case}\n"
                            i=i+1
                        elif i==3:
                            test_cases_text += "IN THE TESTING, THERE IS MORE\n"
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
            raise ValueError(f"从MBPPPlus数据中提取问题时出错: {e}")    
    def _extract_function_signature(self, code: str) -> str:
        """
        从代码中提取函数签名（函数定义行）。
        """
        lines = code.strip().split('\n')
        for line in lines:
            if line.strip().startswith('def '):
                # 找到函数定义行
                # 如果有多行参数，继续读取
                signature = line
                if not line.rstrip().endswith(':'):
                    # 多行函数定义
                    for next_line in lines[lines.index(line)+1:]:
                        signature += '\n' + next_line
                        if next_line.rstrip().endswith(':'):
                            break
                return signature.strip()
        return "def unknown_function():"
    
    def _extract_function_name(self, code: str) -> str:
        """
        从代码中提取函数名。
        """
        # 使用正则表达式查找函数定义
        match = re.search(r'def\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)
        return None
    
    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个MBPP+问题的完整数据用于执行和验证。
        包括任务描述、基础测试用例、参考解决方案和扩展测试套件。
        """
        data = self._get_problem_by_index(index)
        
        # 调试信息
        # print(f"[DEBUG] Loading MBPP+ problem at index {index}")
        # print(f"[DEBUG] task_id: {data.get('task_id', 'NOT FOUND')}")
        # func_name = self._extract_function_name(data.get('code', ''))
        # print(f"[DEBUG] function_name: {func_name}")
        # print(f"[DEBUG] Has test_list: {bool(data.get('test_list'))}")
        # print(f"[DEBUG] Has extended test: {bool(data.get('test'))}")
        
        return data
    
    def _prepare_execution_environment(self):
        """
        准备执行环境，预导入常用模块。
        """
        import builtins
        import math
        import re as regex_module
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
        from typing import List, Dict, Tuple, Any, Optional, Set
        
        return {
            '__builtins__': builtins,
            'math': math,
            're': regex_module,
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
            # 添加collections的常用类
            'Counter': collections.Counter,
            'defaultdict': collections.defaultdict,
            'deque': collections.deque,
            'OrderedDict': collections.OrderedDict,
            # 添加类型提示
            'List': List,
            'Dict': Dict,
            'Tuple': Tuple,
            'Set': Set,
            'Any': Any,
            'Optional': Optional,
        }
    
    def _execute_basic_tests(self, code: str, test_cases: List[str]) -> tuple[bool, str]:
        """
        执行基础测试用例（test_list中的assert语句）。
        
        Returns: (all_passed, error_message)
        """
        exec_globals = self._prepare_execution_environment()
        
        try:
            # 执行生成的代码
            exec(code, exec_globals)
            
            # 运行每个测试用例
            failed_tests = []
            for i, test_case in enumerate(test_cases):
                try:
                    # 执行assert语句
                    exec(test_case, exec_globals)
                except AssertionError as e:
                    failed_tests.append(f"Test {i+1} failed: {test_case}")
                except Exception as e:
                    failed_tests.append(f"Error in test {i+1}: {str(e)}")
            
            if failed_tests:
                return False, "\n".join(failed_tests)
            return True, "All basic tests passed"
            
        except SyntaxError as e:
            return False, f"Syntax error in code: {str(e)}"
        except Exception as e:
            return False, f"Runtime error: {str(e)}\n{traceback.format_exc()}"
    
    def _execute_extended_test(self, code: str, test_code: str, test_imports: List[str]) -> tuple[bool, str]:
        """
        执行扩展测试套件（test字段中的完整测试代码）。
        
        MBPP+的扩展测试包含：
        - assertion函数定义
        - inputs和results列表
        - 循环执行所有测试用例
        """
        exec_globals = self._prepare_execution_environment()
        
        try:
            # 先执行测试所需的导入
            if test_imports:
                for import_stmt in test_imports:
                    exec(import_stmt, exec_globals)
            
            # 执行生成的代码
            exec(code, exec_globals)
            
            # 执行完整的测试代码
            # 测试代码会调用assertion函数验证所有测试用例
            exec(test_code, exec_globals)
            
            return True, "All extended tests passed"
            
        except AssertionError as e:
            # 解析错误信息以提供更好的反馈
            error_msg = str(e)
            if "out:" in error_msg and "exp:" in error_msg:
                return False, f"Extended test failed - {error_msg}"
            return False, f"Extended test assertion failed: {error_msg}"
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Extended test execution error: {str(e)}"
    
    def _extract_code_from_response(self, response: str) -> str:
        """
        从模型响应中提取Python代码，处理各种可能的格式。
        """
        # 移除尾部多余的换行
        response = response.rstrip('\n')
        
        # 方法1：提取markdown Python代码块
        python_blocks = re.findall(r'```python\s*\n(.*?)```', response, re.DOTALL)
        if python_blocks:
            # 返回最后一个代码块（通常是最完整的）
            code = python_blocks[-1]
            while code.endswith('\n\n'):
                code = code[:-1]
            return code
        
        # 方法2：提取通用代码块
        code_blocks = re.findall(r'```\s*\n(.*?)```', response, re.DOTALL)
        if code_blocks:
            code = code_blocks[-1]
            # 检查是否有语言标识符
            lines = code.split('\n')
            if lines and lines[0].strip().lower() in ['python', 'py']:
                code = '\n'.join(lines[1:])
            while code.endswith('\n\n'):
                code = code[:-1]
            return code
        
        # 方法3：查找函数定义（不在代码块中）
        lines = response.split('\n')
        code_lines = []
        in_function = False
        current_indent = 0
        
        for line in lines:
            # 查找函数定义开始
            if re.match(r'^def\s+\w+\s*\(', line.strip()):
                in_function = True
                current_indent = len(line) - len(line.lstrip())
                code_lines = [line]
            elif in_function:
                # 检查是否还在函数内
                if line.strip() and not line[0].isspace():
                    # 顶级非空行，函数结束
                    if not line.strip().startswith('#'):
                        break
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines)
        
        # 最后的备选：返回整个响应
        return response
    
    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型输出是否正确解决MBPP+问题。
        
        评判流程：
        1. 提取生成的代码
        2. 首先运行基础测试用例（test_list）
        3. 如果基础测试通过，运行扩展测试套件（test）
        4. 只有所有测试都通过才返回True
        """
        if not model_output or not ground_truth_data:
            print("[MBPP+] Missing model output or ground truth data")
            return False
        
        # 转换输出为字符串并提取代码
        output_str = str(model_output)
        generated_code = self._extract_code_from_response(output_str)
        
        if not generated_code:
            print("[MBPP+] No code found in model output")
            return False
        
        # 获取测试组件
        test_cases = ground_truth_data.get('test_list', [])
        extended_test = ground_truth_data.get('test', '')
        test_imports = ground_truth_data.get('test_imports', [])
        
        # 步骤1：运行基础测试用例
        if test_cases:
            print(f"[MBPP+] Running {len(test_cases)} basic test cases...")
            passed, error_msg = self._execute_basic_tests(generated_code, test_cases)
            if not passed:
                print(f"[MBPP+] Basic tests failed: {error_msg}")
                return False
            print("[MBPP+] Basic tests passed ✓")
        
        # 步骤2：运行扩展测试套件
        if extended_test:
            print("[MBPP+] Running extended test suite...")
            
            # 从参考代码中提取函数名，并替换测试代码中的函数调用
            reference_code = ground_truth_data.get('code', '')
            expected_func_name = self._extract_function_name(reference_code)
            actual_func_name = self._extract_function_name(generated_code)
            
            # 如果函数名不同，需要在测试代码中替换
            test_code_to_run = extended_test
            if expected_func_name and actual_func_name and expected_func_name != actual_func_name:
                # 替换测试代码中的函数名
                test_code_to_run = test_code_to_run.replace(
                    f"assertion({expected_func_name}",
                    f"assertion({actual_func_name}"
                )
                test_code_to_run = test_code_to_run.replace(
                    f"candidate={expected_func_name}",
                    f"candidate={actual_func_name}"
                )
            
            passed, error_msg = self._execute_extended_test(
                generated_code, 
                test_code_to_run, 
                test_imports
            )
            
            if not passed:
                print(f"[MBPP+] Extended tests failed: {error_msg}")
                return False
            print("[MBPP+] Extended tests passed ✓")
        
        print("[MBPP+] All tests passed successfully! ✅")
        return True