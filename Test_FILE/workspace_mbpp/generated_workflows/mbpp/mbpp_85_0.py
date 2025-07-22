# Workflow ID: mbpp_85_0
# Benchmark: mbpp
# Data Indices: [47, 370]

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
        This is a workflow graph for code generation using iterative refinement (Test-Fix loop).
        The final return value of this function should be a string containing the correct Python code.
        """
        # Step 1: Generate an initial solution
        initial_code = await self.code_generate(instruction="Provide a straightforward solution to swap every n-th and (n+1)th element in a list.")

        # Step 2: Iterative refinement loop - test and fix up to 3 times
        current_code = initial_code
        for iteration in range(3):  # Loop 3 times max for refinement
            test_result = await self.code_runner(code_to_test=current_code)
            
            if test_result.is_correct:
                # Success! Return the working code
                return current_code
            
            # If it fails, use the error message to guide a fix
            current_code = await self.code_fix(
                code=current_code,
                error_message=test_result.error_message
            )

        # If we exit the loop without success, return the last attempt (may still work or be close)
        return current_code