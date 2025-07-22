# Workflow ID: mbpp_10_0
# Benchmark: mbpp
# Data Indices: [22]

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
        # Diverse Strategy: Use FlexibleCustom with "test_driven" pattern to build solution incrementally
        # This avoids hardcoding a single answer and instead builds robustly based on test feedback
        code = await self.flexible_custom(
            custom_instruction="Start with minimal implementation that passes basic tests, then refine.",
            generation_pattern="test_driven",
            strategies=["understand_tests", "implement_minimum", "refactor"]
        )

        # Run the generated code to check correctness
        test_result = await self.code_runner(code_to_test=code)

        # If it fails, attempt to fix using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=code, error_message=test_result.error_message)
            # Re-test the fixed version
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # Optional: fallback to ensemble if still failing (adds diversity)
                solutions = [
                    await self.code_generate(instruction="Use map with lambda to compute powers"),
                    fixed_code,
                    await self.code_generate(instruction="Implement with list comprehension and lambda")
                ]
                code = await self.sc_ensemble(solutions=solutions)
                test_result = await self.code_runner(code_to_test=code)

        return code