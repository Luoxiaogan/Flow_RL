"""
Lightweight code executor for safe Python code execution.
This module is designed to be imported by ProcessPoolExecutor without heavy dependencies.
"""

import sys
import ast
import traceback
from typing import Tuple, List


def check_code_safety(code: str, disallowed_imports: List[str]) -> Tuple[bool, str]:
    """
    Check if the code is safe to execute.

    Args:
        code: Python code to check
        disallowed_imports: List of module names that are not allowed

    Returns:
        Tuple of (is_safe, error_message)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error: {e}"

    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    if module_name in disallowed_imports:
                        return False, f"Import of '{module_name}' is not allowed"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    if module_name in disallowed_imports:
                        return False, f"Import from '{module_name}' is not allowed"

        # Check dangerous functions
        if isinstance(node, ast.Name):
            if node.id in ['eval', 'exec', '__import__', 'compile', 'open']:
                return False, f"Use of '{node.id}' is not allowed"

        # Check attribute access for dangerous operations
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                if node.value.id == '__builtins__':
                    return False, "Access to __builtins__ is not allowed"

    return True, None


def run_code(code: str, timeout: int = 30) -> Tuple[str, str]:
    """
    Execute Python code safely in an isolated namespace.

    Args:
        code: Python code string to execute
        timeout: Maximum execution time (handled by caller)

    Returns:
        Tuple[str, str]: (status, result/error_message)
    """
    try:
        # Create isolated namespace with limited builtins
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
            'bin': bin, 'bool': bool, 'bytearray': bytearray, 'bytes': bytes,
            'chr': chr, 'complex': complex, 'dict': dict, 'divmod': divmod,
            'enumerate': enumerate, 'filter': filter, 'float': float,
            'format': format, 'frozenset': frozenset, 'hex': hex,
            'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
            'iter': iter, 'len': len, 'list': list, 'map': map,
            'max': max, 'min': min, 'next': next, 'oct': oct,
            'ord': ord, 'pow': pow, 'print': print, 'range': range,
            'repr': repr, 'reversed': reversed, 'round': round,
            'set': set, 'slice': slice, 'sorted': sorted, 'str': str,
            'sum': sum, 'super': super, 'tuple': tuple, 'type': type,
            'zip': zip,
            # Math functions
            '__import__': lambda name, *args, **kwargs: __import__(name) if name in ['math', 'itertools', 'collections', 'functools', 'random'] else None,
        }

        global_namespace = {'__builtins__': safe_builtins}

        # Prohibited imports for safety
        disallowed_imports = [
            "os", "sys", "subprocess", "multiprocessing",
            "matplotlib", "seaborn", "plotly", "bokeh", "ggplot",
            "pylab", "tkinter", "PyQt5", "wx", "pyglet",
            "socket", "urllib", "requests", "http"
        ]

        # AST safety check
        is_safe, error_msg = check_code_safety(code, disallowed_imports)
        if not is_safe:
            return "Error", error_msg

        # Execute code
        exec(code, global_namespace)

        # Look for 'solve' function
        if 'solve' in global_namespace and callable(global_namespace['solve']):
            result = global_namespace['solve']()
            return "Success", str(result)
        else:
            return "Error", "Function 'solve' not found"

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_str = traceback.format_exception(exc_type, exc_value, exc_traceback)
        return "Error", f"Execution error: {str(e)}\n{''.join(tb_str)}"


if __name__ == "__main__":
    # Test the executor
    test_code = """
def solve():
    return sum(range(1, 11))
"""
    status, result = run_code(test_code)
    print(f"Status: {status}")
    print(f"Result: {result}")