# 文件: ScoreFlow/scripts/utils/code_executor.py
# 这是一个新的共享工具文件，用于存放代码执行相关的函数。

import traceback
import multiprocessing
from typing import List

def unsafe_execute(code: str, tests: List[str], result_queue: multiprocessing.Queue):
    """
    在受限环境中执行代码并运行测试用例。
    这个函数现在是独立的，可以被任何模块安全地导入。
    警告：尽管在子进程中运行，exec 仍然存在安全风险。
    """
    try:
        # 创建一个执行命名空间
        exec_globals = {}
        # 将生成的代码和所有测试代码拼接在一起
        # MBPP的测试用例已经是 "assert ..." 的形式
        full_code = code + "\n\n" + "\n".join(tests)
        
        # 执行代码
        exec(full_code, exec_globals)
        
        # 如果没有异常，说明所有 assert 都通过了
        result_queue.put(("success", "All tests passed."))
    except Exception:
        # 捕获任何异常（包括 AssertionError），并将其作为失败信息返回
        error_info = traceback.format_exc()
        result_queue.put(("failure", error_info))