# ### 修改点 1: 不再需要 traceback，因为它已移至 unsafe_execute 内部 ###
# import traceback 
import contextlib
import io
import multiprocessing
import signal
from typing import List, Dict, Any, Tuple

# 导入基类
from ScoreFlow.scripts.base_handler import BenchmarkHandler
# ### 修改点 2: 从共享的 utils 模块导入 unsafe_execute 函数 ###
from ScoreFlow.scripts.utils.code_executor import unsafe_execute

# ### 修改点 3: 移除整个本地的 unsafe_execute 函数定义 ###
# def unsafe_execute(code: str, tests: List[str], result_queue: multiprocessing.Queue):
#     """
#     ... 此函数已被移至 ScoreFlow/scripts/utils/code_executor.py ...
#     """
#     pass

class MbppHandler(BenchmarkHandler):
    """
    MBPP (Mostly Basic Python Programming) 数据集的具体处理器。
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        从 MBPP 数据中提取问题描述文本（'text'字段）。
        
        格式:
        Problem 1:
        [problem description text]

        Problem 2:
        [problem description text]
        ...
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            # MBPP 的问题描述在 'text' 字段中
            return "\n\n".join([f"Problem {i+1}:\n{p['text']}" for i, p in enumerate(problems)])
        except (KeyError, IndexError) as e:
            raise ValueError(f"从MBPP数据中提取问题时出错: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        获取单个 MBPP 问题的完整数据，用于后续的执行和验证。
        """
        return self._get_problem_by_index(index)

    def _execute_and_test(self, generated_code: str, test_list: List[str], timeout: int = 5) -> Tuple[bool, str]:
        """
        在一个独立的、有时间限制的进程中执行生成的代码并验证测试用例。
        """
        if not generated_code or not test_list:
            return False, "Generated code or test list is empty."

        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=unsafe_execute, # 这里现在使用的是从外部导入的函数
            args=(generated_code, test_list, result_queue)
        )
        
        process.start()
        process.join(timeout=timeout)

        if process.is_alive():
            # 超时，终止进程
            process.terminate()
            process.join()
            return False, f"Execution timed out after {timeout} seconds."

        if process.exitcode != 0:
            return False, f"Execution process exited with non-zero code: {process.exitcode}."
        
        try:
            status, message = result_queue.get_nowait()
            return status == "success", message
        except multiprocessing.queues.Empty:
            return False, "Result queue was empty. Unknown execution error."


    def judge(self, model_output: Any, ground_truth_data: Dict[str, Any]) -> bool:
        """
        评判模型生成的代码是否能通过 MBPP 的单元测试。
        
        1. `model_output` 应该是一个包含 Python 代码的字符串。
        2. `ground_truth_data` 是完整的 MBPP 问题条目，包含 'test_list'。
        """
        try:
            # 假设 model_output 是一个 workflow 的最终产出，它是一个包含 Python 代码的字符串
            generated_code = str(model_output)
            
            # 从标准答案数据中获取测试用例列表
            test_list = ground_truth_data.get('test_list')
            if not test_list:
                # 如果没有测试用例，我们无法验证，判定为失败
                return False

            # 执行代码并进行测试
            is_correct, message = self._execute_and_test(generated_code, test_list)
            
            if not is_correct:
                # 打印失败信息以便调试
                # 为了保持输出简洁，可以注释掉这行
                # print(f"MBPP Judge: Test failed. Reason: {message}")
                pass
            
            return is_correct

        except Exception as e:
            print(f"MBPP Judge: An unexpected error occurred during judgment: {e}")
            return False