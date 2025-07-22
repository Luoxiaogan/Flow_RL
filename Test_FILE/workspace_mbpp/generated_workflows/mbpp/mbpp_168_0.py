# Workflow ID: mbpp_168_0
# Benchmark: mbpp
# Data Indices: [197]

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
        # Use the FlexibleCustom operator with a "test_driven" pattern to build the solution incrementally
        # This ensures we focus on correctness first, then optimize — aligning with efficiency goals
        code = await self.flexible_custom(
            custom_instruction="Implement a solution that passes all test cases incrementally.",
            generation_pattern="test_driven",
            strategies=["understand_tests", "implement_minimum", "refactor"],
            max_refinements=1
        )

        # Run the generated code to check correctness
        test_result = await self.code_runner(code_to_test=code)

        # If it fails, attempt to fix using the error message
        if not test_result.is_correct:
            code = await self.code_fix(code=code, error_message=test_result.error_message)

            # Re-run after fixing
            test_result = await self.code_runner(code_to_test=code)

        # Return the final code (either original or fixed)
        return code