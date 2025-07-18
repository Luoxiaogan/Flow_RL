# Workflow ID: mbpp_3
# Benchmark: mbpp
# Data Indices: [4, 6]

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

    async def run_workflow(self):
        """
        This is a workflow graph for code generation.
        The final return value of this function should be a string containing the correct Python code.
        """
        # Generate initial solution
        initial_code = await self.code_generate(instruction="Write a Python function to check if a number is prime.")

        # Test the initial solution
        test_result = await self.code_runner(code_to_test=initial_code)

        # If the code fails, attempt to fix it
        if not test_result.is_correct:
            # Use CodeFix to generate a corrected version based on the error message
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            return fixed_code

        # If the code passes, return it
        return initial_code