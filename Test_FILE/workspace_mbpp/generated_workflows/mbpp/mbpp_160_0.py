# Workflow ID: mbpp_160_0
# Benchmark: mbpp
# Data Indices: [210]

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
        # --- Diverse and Efficient Workflow: Generate-Test-Fix with Single Iteration ---
        # Use a simple yet effective pattern that avoids redundancy while still being robust.
        initial_code = await self.code_generate(instruction="Write a concise and efficient function to compare two lists of tuples. Ensure it handles edge cases like empty lists or mismatched lengths.")
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # If it fails, attempt to fix using the error message — ensures responsiveness to failures
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed version to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # Fallback to ensemble if fix still fails — introduces diversity in recovery strategy
                solutions = [
                    initial_code,
                    fixed_code,
                    await self.code_generate(instruction="Try an alternative approach using set comparison for efficiency.")
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code
        
        # If the first attempt passes, return it directly — efficient baseline
        return initial_code