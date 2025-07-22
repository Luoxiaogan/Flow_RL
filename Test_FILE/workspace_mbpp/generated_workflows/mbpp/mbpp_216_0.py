# Workflow ID: mbpp_216_0
# Benchmark: mbpp
# Data Indices: [127, 28]

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
        # Step 1: Generate initial solution
        code = await self.code_generate(instruction="Provide a straightforward solution to sum elements in two lists.")

        # Step 2: Iterative refinement loop (2-3 times)
        for attempt in range(2):  # Loop 2 times for refinement
            test_result = await self.code_runner(code_to_test=code)
            
            if test_result.is_correct:
                # Success! Exit early
                return code
            
            # If failed, fix the code based on error message
            code = await self.code_fix(code=code, error_message=test_result.error_message)
        
        # Final test after refinement loop
        final_test = await self.code_runner(code_to_test=code)
        if not final_test.is_correct:
            # One last fallback: generate a new approach using flexible custom with modular strategy
            code = await self.flexible_custom(
                custom_instruction="Generate a robust solution by decomposing the problem into helper functions.",
                previous_results=[code]
            )
        
        return code