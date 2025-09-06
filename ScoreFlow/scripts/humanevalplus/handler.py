## HumanevalplusHandler (handler.py)

from typing import List, Dict, Any
import ast
import traceback
import asyncio
import sys
from io import StringIO
import contextlib

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler

class HumanevalplusHandler(BenchmarkHandler):
    """
    HumanEval+ dataset handler.
    
    Handles code generation tasks with enhanced test coverage compared to original HumanEval.
    Requires generating Python functions that pass comprehensive test suites.
    """
    
    def get_prompt_text(self, indices: List[int]) -> str:
        """
        Extract function signatures and specifications from HumanEval+ data and format them clearly.
        
        Format:
        ---
        **FUNCTION SIGNATURE AND SPECIFICATION:**
        [prompt with docstring]
        
        **ENTRY POINT:**
        Function name: [entry_point]
        
        **CANONICAL SOLUTION (Reference):**
        [canonical solution if available]
        ---
        
        (If multiple indices are provided, this structure repeats)
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            formatted_problems = []
            
            for problem in problems:
                # Extract prompt (contains function signature and docstring) and entry point
                prompt = problem.get('prompt', '')
                entry_point = problem.get('entry_point', '')
                canonical_solution = problem.get('canonical_solution', '')
                
                # Include canonical solution if available (for reference, not to copy)
                canonical_text = ""
                if canonical_solution:
                    canonical_text = f"\n**CANONICAL SOLUTION (Reference - DO NOT COPY):**\n```python\n{canonical_solution}\n```"
                
                # Combine problem components
                formatted_problem = f"""---
**FUNCTION SIGNATURE AND SPECIFICATION:**
{prompt}

**ENTRY POINT:**
Function name: {entry_point}
{canonical_text}
---"""
                formatted_problems.append(formatted_problem)
            
            return "\n\n".join(formatted_problems)
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting problem from HumanEval+ data: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        Get complete data for a single HumanEval+ problem for execution and verification.
        This includes prompt, test cases, canonical solution, and enhanced test suite.
        """
        return self._get_problem_by_index(index)
    
    def _execute_code_with_tests(self, code: str, test_code: str, entry_point: str) -> tuple[bool, str]:
        """
        Safely execute code and run HumanEval+ format test cases.
        
        HumanEval+ tests are wrapped in a check(candidate) function, requiring:
        1. Execute generated code to define the function
        2. Execute test code to define check function
        3. Call check function with the generated function
        
        Returns: (all_passed, error_message)
        """
        # Create execution environment
        import builtins
        
        # Pre-import commonly used modules
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
            'List': List,
            'Dict': Dict,
            'Tuple': Tuple,
            'Any': Any,
            'Optional': Optional,
        }
        
        try:
            # Execute the generated code to define the function
            exec(code, exec_globals)
            
            # Check if the function was defined
            if entry_point not in exec_globals:
                return False, f"Function '{entry_point}' was not defined in the code"
            
            # Execute the test code to define check function
            exec(test_code, exec_globals)
            
            # Check if check function exists
            if 'check' not in exec_globals:
                return False, "Test check function was not defined"
            
            # Run the check function with the generated function
            check_func = exec_globals['check']
            candidate_func = exec_globals[entry_point]
            
            # Capture output and run tests
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                check_func(candidate_func)
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                
                # If we reach here without exception, tests passed
                return True, "All tests passed"
                
            except AssertionError as e:
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                return False, f"Test assertion failed: {str(e)}\nOutput: {output}"
            except Exception as e:
                output = sys.stdout.getvalue()
                sys.stdout = old_stdout
                return False, f"Test execution error: {str(e)}\nOutput: {output}"
                
        except SyntaxError as e:
            return False, f"Syntax error in code: {str(e)}"
        except Exception as e:
            return False, f"Runtime error: {str(e)}\n{traceback.format_exc()}"
    
    async def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        Judge whether the model output correctly solves the HumanEval+ problem.
        
        For HumanEval+, we need to:
        1. Extract the generated code from the output
        2. Run it against the enhanced test suite
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
        
        # Get entry point and test code
        entry_point = ground_truth_data.get('entry_point', '')
        test_code = ground_truth_data.get('test', '')
        
        if not entry_point or not test_code:
            print("Missing entry point or test code")
            return False
        
        # Execute and verify
        passed, error_msg = self._execute_code_with_tests(code, test_code, entry_point)
        
        if not passed:
            print(f"Tests failed: {error_msg}")
            
        return passed
    
    def _extract_code(self, text: str) -> str:
        """
        Extract Python code from text, looking for code blocks or function definitions.
        """
        import re
        
        # Try to find ```python blocks
        python_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        if python_blocks:
            return python_blocks[-1]  # Return last code block
        
        # Try to find ``` blocks
        code_blocks = re.findall(r'```\n(.*?)\n```', text, re.DOTALL)
        if code_blocks:
            return code_blocks[-1]
        
        # Try to extract function definition
        # Look for everything from 'def' or 'from typing' to the end of the function
        if 'def ' in text:
            lines = text.split('\n')
            code_lines = []
            in_function = False
            indent_level = 0
            
            for line in lines:
                # Start collecting from imports or function definition
                if ('from typing import' in line or 
                    'import ' in line or 
                    line.strip().startswith('def ')):
                    in_function = True
                    if line.strip().startswith('def '):
                        # Track indentation level of function
                        indent_level = len(line) - len(line.lstrip())
                    code_lines.append(line)
                elif in_function:
                    # Continue collecting lines that are part of the function
                    if line.strip() == '':
                        code_lines.append(line)
                    elif line.strip().startswith('#'):
                        code_lines.append(line)
                    elif len(line) - len(line.lstrip()) > indent_level or line.strip() != '':
                        code_lines.append(line)
                    else:
                        # Non-indented non-empty line after function, stop
                        if not line.strip().startswith('def '):
                            break
                        code_lines.append(line)
            
            if code_lines:
                return '\n'.join(code_lines)
        
        return ""