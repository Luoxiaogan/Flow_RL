# Workflow ID: mbpp_115_0
# Benchmark: mbpp
# Data Indices: [58, 304]

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
        This is a workflow graph for code generation using the Parallel Ensemble & Test pattern.
        It generates multiple diverse solutions, selects the best one via ensemble, and verifies it with testing.
        """
        # Generate two different solutions using varied instructions to ensure diversity
        solution1 = await self.code_generate(instruction="Write a function that iterates through the list and identifies duplicates by tracking seen elements.")
        solution2 = await self.code_generate(instruction="Implement a solution using a dictionary to count occurrences of each integer, then print those with counts > 1.")

        # Use ScEnsemble to select the best candidate from the two generated solutions
        selected_code = await self.sc_ensemble(solutions=[solution1, solution2])

        # Run the final selected code through the test suite to verify correctness
        test_result = await self.code_runner(code_to_test=selected_code)

        # If the selected code fails, attempt to fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=selected_code, error_message=test_result.error_message)
            # Re-test the fixed version to ensure it now passes
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # As a fallback, generate a new solution using a flexible custom approach (e.g., modular)
                fallback_code = await self.flexible_custom(
                    custom_instruction="Break down the problem into helper functions: one to count, another to filter, and a third to print.",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                # Final test of fallback solution
                final_test = await self.code_runner(code_to_test=fallback_code)
                return fallback_code if final_test.is_correct else fallback_code

        # If the original selected code passed, return it
        return selected_code