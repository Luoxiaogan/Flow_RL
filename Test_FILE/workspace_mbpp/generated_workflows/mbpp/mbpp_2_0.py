# Workflow ID: mbpp_2_0
# Benchmark: mbpp
# Data Indices: [244]

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
        # Use Generate-Test-Fix pattern as required
        initial_code = await self.code_generate(instruction="Provide a straightforward solution to count digits in factorial of a given number.")
        test_result = await self.code_runner(code_to_test=initial_code)

        if not test_result.is_correct:
            # Fix the code using the error message from the failed test
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed code
            test_result = await self.code_runner(code_to_test=fixed_code)

            # If still failing after one fix, we might need more iterations — but per task, just one fix is sufficient
            # For correctness, we return the fixed version even if it fails again (in practice, this would loop)
            return fixed_code

        # If initial code passed, return it
        return initial_code