# Workflow ID: mbpp_39_0
# Benchmark: mbpp
# Data Indices: [170]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        # --- Initialize your chosen operators here ---
        self.code_generate = operator.CustomCodeGenerate(self.config, self.problem)
        self.code_runner = operator.CodeRunner(self.config, self.problem)
        self.code_fix = operator.CodeFix(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for code generation.
        The final return value of this function should be a string containing the correct Python code.
        """
        # Use Generate-Test-Fix pattern as instructed
        initial_code = await self.code_generate(instruction="Write a function to check if the given expression is balanced or not. Be explicit in handling parentheses, brackets, and braces.")
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # Apply fix using error message from failed test
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed code
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if not retest_result.is_correct:
                # If still failing, try one more time with a different instruction
                fallback_code = await self.code_generate(instruction="Rewrite the solution focusing on edge cases like empty strings, unmatched brackets, and nested structures.")
                final_test = await self.code_runner(code_to_test=fallback_code)
                if not final_test.is_correct:
                    # As last resort, use the fixed version from first fix attempt
                    return fixed_code
                return fallback_code
            return fixed_code
        
        return initial_code