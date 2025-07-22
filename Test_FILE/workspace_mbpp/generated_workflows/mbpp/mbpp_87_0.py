# Workflow ID: mbpp_87_0
# Benchmark: mbpp
# Data Indices: [371]

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
        # Use a flexible custom operator with a modular strategy to generate a clean, reusable solution
        modular_code = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps: take two tuples and nest them.",
            generation_pattern="modular",
            strategies=["decompose_problem", "implement_helpers", "combine_solution"]
        )

        # Run the test to check correctness
        test_result = await self.code_runner(code_to_test=modular_code)

        # If it fails, attempt to fix based on the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=modular_code,
                error_message=test_result.error_message
            )
            # Re-test the fixed version
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # As a fallback, try a simple direct generation (baseline strategy)
                final_code = await self.code_generate(instruction="Write a minimal function that concatenates two tuples into a nested tuple.")
                return final_code
            return fixed_code

        # If it passes, return the modular solution
        return modular_code