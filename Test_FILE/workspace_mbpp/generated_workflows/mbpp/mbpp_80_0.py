# Workflow ID: mbpp_80_0
# Benchmark: mbpp
# Data Indices: [278]

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
        # Use iterative refinement with Test-Fix loop (2-3 iterations)
        initial_code = await self.code_generate(instruction="Write a regex pattern that matches strings starting with 'a', followed by any characters, and ending with 'b'.")
        
        for attempt in range(3):  # Loop for 2-3 times as instructed
            test_result = await self.code_runner(code_to_test=initial_code)
            
            if test_result.is_correct:
                return initial_code  # Success! Return the working code
            
            # If it fails, fix based on error message
            initial_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
        
        # If we exit the loop without success, return the last fixed version
        return initial_code