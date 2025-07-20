import multiprocessing
from typing import List, Dict, Any, Tuple

# Import base class
from ScoreFlow.scripts.base_handler import BenchmarkHandler
# Import shared unsafe_execute function
from ScoreFlow.scripts.utils.code_executor import unsafe_execute

class HumanevalHandler(BenchmarkHandler):
    """
    HumanEval dataset handler.
    
    HumanEval is a benchmark for measuring functional correctness of code generation.
    Each problem includes a function signature, docstring, and test cases.
    """

    def get_prompt_text(self, indices: List[int]) -> str:
        """
        Extract problem descriptions from HumanEval data.
        
        Format:
        Problem 1:
        [function signature with docstring]
        
        Problem 2:
        [function signature with docstring]
        ...
        """
        try:
            problems = [self._get_problem_by_index(i) for i in indices]
            # HumanEval problems are in the 'prompt' field (includes function signature and docstring)
            return "\n\n".join([f"Problem {i+1}:\n{p['prompt']}" for i, p in enumerate(problems)])
        except (KeyError, IndexError) as e:
            raise ValueError(f"Error extracting problems from HumanEval data: {e}")

    def get_verification_data(self, index: int) -> Dict[str, Any]:
        """
        Get complete HumanEval problem data for execution and verification.
        """
        return self._get_problem_by_index(index)

    def _execute_and_test(self, generated_code: str, test_code: str, entry_point: str, timeout: int = 5) -> Tuple[bool, str]:
        """
        Execute generated code and run test cases in an isolated process.
        
        :param generated_code: The generated solution code
        :param test_code: The test code containing check function and assertions
        :param entry_point: The function name that should be tested
        :param timeout: Maximum execution time in seconds
        :return: (success, message) tuple
        """
        if not generated_code or not test_code:
            return False, "Generated code or test code is empty."

        # Extract test assertions from the test code
        # The test code contains a check() function with assertions
        test_lines = test_code.strip().split('\n')
        test_assertions = []
        
        # Find the check function and extract its assertions
        in_check_function = False
        for line in test_lines:
            if 'def check(candidate):' in line:
                in_check_function = True
                continue
            if in_check_function:
                stripped = line.strip()
                if stripped.startswith('assert'):
                    # Replace 'candidate' with the actual entry point name
                    test_assertions.append(stripped.replace('candidate', entry_point))
                elif stripped and not stripped.startswith('#') and not line.startswith(' ') and not line.startswith('\t'):
                    # Exit check function if we hit non-indented code
                    break

        if not test_assertions:
            return False, "No test assertions found in test code."

        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(
            target=unsafe_execute,
            args=(generated_code, test_assertions, result_queue)
        )
        
        process.start()
        process.join(timeout=timeout)

        if process.is_alive():
            # Timeout - terminate the process
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
        Judge if the model-generated code passes the HumanEval test cases.
        
        :param model_output: The generated code (string)
        :param ground_truth_data: Complete HumanEval problem entry including 'test' field
        :return: True if all tests pass, False otherwise
        """
        try:
            # Model output should be a string containing Python code
            generated_code = str(model_output)
            
            # Get test code and entry point from ground truth data
            test_code = ground_truth_data.get('test')
            entry_point = ground_truth_data.get('entry_point')
            
            if not test_code or not entry_point:
                # Missing required fields
                return False

            # Execute code and run tests
            is_correct, message = self._execute_and_test(
                generated_code, 
                test_code, 
                entry_point,
                timeout=10  # Give more time for complex problems
            )
            
            if not is_correct:
                # Optionally log failure for debugging
                # print(f"HumanEval Judge: Test failed. Reason: {message}")
                pass
            
            return is_correct

        except Exception as e:
            print(f"HumanEval Judge: An unexpected error occurred during judgment: {e}")
            return False