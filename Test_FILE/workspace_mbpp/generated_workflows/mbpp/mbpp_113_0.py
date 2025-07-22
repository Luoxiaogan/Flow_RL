# Workflow ID: mbpp_113_0
# Benchmark: mbpp
# Data Indices: [20]

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
        initial_code = await self.code_generate(instruction="Solve the problem step-by-step, explaining your reasoning clearly in comments.")
        test_result = await self.code_runner(code_to_test=initial_code)

        if not test_result.is_correct:
            # Fix the code using the error message from the failed test
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed code to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if not retest_result.is_correct:
                # If still failing, use a second round of fixing (optional safety net)
                final_code = await self.code_fix(code=fixed_code, error_message=retest_result.error_message)
                return final_code
            return fixed_code

        return initial_code