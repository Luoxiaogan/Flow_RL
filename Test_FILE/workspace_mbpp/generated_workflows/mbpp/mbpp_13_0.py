# Workflow ID: mbpp_13_0
# Benchmark: mbpp
# Data Indices: [201]

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
        initial_code = await self.code_generate(instruction="Write a Python function to count rotations needed to make an array sorted. Explain reasoning in comments.")
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # Apply fix based on error message from test runner
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Re-run the fixed code to ensure correctness
            final_test = await self.code_runner(code_to_test=fixed_code)
            if not final_test.is_correct:
                # If still failing, we may need more refinement — but per instructions, just one fix is expected
                # In practice, this could loop, but the task specifies "use Generate-Test-Fix"
                pass
            return fixed_code
        
        return initial_code