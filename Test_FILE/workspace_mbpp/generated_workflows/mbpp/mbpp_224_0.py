# Workflow ID: mbpp_224_0
# Benchmark: mbpp
# Data Indices: [133, 111]

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
        code = await self.code_generate(instruction="Provide a straightforward solution to the problem.")

        # Step 2: Iterative refinement loop (2-3 times) — core diversity pattern
        for iteration in range(3):  # Loop 3 times max for robustness
            test_result = await self.code_runner(code_to_test=code)
            
            if test_result.is_correct:
                # Success! Return the working code
                return code
            
            # If not correct, fix based on error message
            code = await self.code_fix(
                code=code,
                error_message=test_result.error_message
            )
        
        # Final fallback: If still failing after 3 iterations, return last fixed version
        return code