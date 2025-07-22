# Workflow ID: mbpp_184_0
# Benchmark: mbpp
# Data Indices: [194]

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
        This is a workflow graph for code generation using iterative refinement.
        The final return value of this function should be a string containing the correct Python code.
        """
        # Step 1: Generate an initial solution
        code = await self.code_generate(instruction="Provide a straightforward implementation using heapq to find the n cheapest items.")

        # Step 2: Iteratively test and fix up to 3 times
        for iteration in range(3):
            test_result = await self.code_runner(code_to_test=code)
            if test_result.is_correct:
                return code  # Success! Return the working code
            
            # If it fails, use the error message to generate a fix
            code = await self.code_fix(code=code, error_message=test_result.error_message)

        # If we've exhausted all iterations without success, return the last generated code
        return code