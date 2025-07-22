# Workflow ID: mbpp_30_0
# Benchmark: mbpp
# Data Indices: [320]

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
        # Generate an initial solution using a clear instruction to promote correctness
        initial_code = await self.code_generate(instruction="Write a function that chunks tuples into sub-tuples of size n. Include detailed comments explaining how the chunking works.")

        # Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # If the code fails, use CodeFix to generate a corrected version based on the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed code to ensure it's now correct
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if not retest_result.is_correct:
                # In rare cases where fix doesn't work, fall back to a second fix attempt
                final_code = await self.code_fix(code=fixed_code, error_message=retest_result.error_message)
                return final_code
            return fixed_code

        # If the initial code passes all tests, return it
        return initial_code