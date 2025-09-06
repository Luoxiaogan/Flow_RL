## MbppplusHandler (handler.py)

from typing import List, Dict, Any
import ast
import traceback
import asyncio
import sys
from io import StringIO
import contextlib

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class MbppplusHandler(BenchmarkHandler):
    """
    MBPP+ (Enhanced Mostly Basic Python Problems) dataset handler.
    
    Handles code generation tasks with more comprehensive test cases than original MBPP.
    Requires generating Python functions and validating through extended test suites.
    """
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        Extract programming task descriptions from MBPP+ data and format them clearly for workflow generation.
        
        Format:
        ---
        **TASK:**
        [task description]
        
        **CODE SIGNATURE:**
        [code template/signature if available]
        
        **TEST CASES:**
        [test case 1]
        [test case 2]
        ...
        ---
        
        (If multiple indices are provided, this structure repeats)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # Extract task description and test cases
                task_description = problem.get('prompt', problem.get('text', ''))
                test_cases = problem.get('test_list', [])
                code_template = problem.get('code', '')
                
                # Format test cases
                test_cases_text = "**TEST CASES:**\n"
                if test_cases:
                    for test_case in test_cases:
                        test_cases_text += f"{test_case}\n"
                else:
                    test_cases_text += "No test cases provided.\n"
                
                # Include code signature if available
                code_text = ""
                if code_template:
                    code_text = f"\n**CODE SIGNATURE:**\n```python\n{code_template}\n```\n"
                
                # Combine task description, code template and test cases
                formatted_problem = f"""---
**TASK:**
{task_description}
{code_text}
{test_cases_text.strip()}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting problem from MBPP+ data: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        Get complete data for a single MBPP+ problem for execution and verification.
        This includes task description, test cases, reference solution, and extended test suite.
        """
        return self._get_problem_by_index(index)
    
    def _execute_code_with_tests(self, code: str, test_cases: List[str], test_setup: str = "") -> tuple[bool, str]:
        """
        Safely execute code and run test cases.
        
        Returns: (all_passed, error_message)
        """
        # Create execution environment with necessary built-ins
        import builtins
        
        # Pre-import commonly used standard library modules
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
        import numpy as np
        
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
        }
        
        try:
            # Execute test setup if provided
            if test_setup:
                exec(test_setup, exec_globals)
            
            # Execute the generated code
            exec(code, exec_globals)
            
            # Run each test case
            failed_tests = []
            for test_case in test_cases:
                try:
                    # Execute test case - assert will raise AssertionError if fails
                    exec(test_case, exec_globals)
                except AssertionError as e:
                    failed_tests.append(f"Failed: {test_case} - {str(e)}")
                except Exception as e:
                    failed_tests.append(f"Error in test: {test_case} - {str(e)}")
            
            if failed_tests:
                return False, "\n".join(failed_tests)
            return True, "All tests passed"
            
        except SyntaxError as e:
            return False, f"Syntax error in code: {str(e)}"
        except Exception as e:
            return False, f"Runtime error: {str(e)}\n{traceback.format_exc()}"
    
    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        Judge whether the model output correctly solves the MBPP+ problem.
        
        For MBPP+, we need to:
        1. Extract the generated code from the output
        2. Run it against test cases
        3. Also run against extended test suite if available
        """
        if not model_output or not ground_truth_data:
            return False
        
        # Convert to string
        output_str = str(model_output)
        
        # Try to extract code from the output
        code = self._extract_code(output_str)
        if not code:
            # If no code block found, treat entire output as code
            code = output_str
        
        # Get test cases from ground truth data
        test_cases = ground_truth_data.get('test_list', [])
        
        # Get extended test suite if available (MBPP+ feature)
        extended_test = ground_truth_data.get('test', '')
        test_imports = ground_truth_data.get('test_imports', [])
        
        # First run basic test cases
        if test_cases:
            passed, error_msg = self._execute_code_with_tests(code, test_cases)
            if not passed:
                print(f"Basic tests failed: {error_msg}")
                return False
        
        # If basic tests pass and extended test suite exists, run it
        if extended_test:
            # Prepare test setup with imports
            test_setup = "\n".join(test_imports) if test_imports else ""
            
            # Run extended test as a single comprehensive test
            extended_passed, extended_error = self._execute_code_with_tests(
                code, 
                [extended_test], 
                test_setup
            )
            
            if not extended_passed:
                print(f"Extended tests failed: {extended_error}")
                return False
        
        return True
    
    def _extract_code(self, text: str) -> str:
        """
        Extract Python code from text, looking for code blocks or function definitions.
        """
        # Look for code blocks
        import re
        
        # Try to find ```python blocks
        python_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        if python_blocks:
            return python_blocks[-1]  # Return last code block
        
        # Try to find ``` blocks
        code_blocks = re.findall(r'```\n(.*?)\n```', text, re.DOTALL)
        if code_blocks:
            return code_blocks[-1]
        
        # Try to find function definitions
        lines = text.split('\n')
        code_lines = []
        in_function = False
        
        for line in lines:
            if line.strip().startswith('def '):
                in_function = True
                code_lines = [line]
            elif in_function:
                if line and not line[0].isspace() and not line.strip().startswith('#'):
                    # End of function
                    break
                code_lines.append(line)
        
        if code_lines:
            return '\n'.join(code_lines)
        
        return ""