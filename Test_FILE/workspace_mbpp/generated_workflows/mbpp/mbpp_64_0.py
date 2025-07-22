# Workflow ID: mbpp_64_0
# Benchmark: mbpp
# Data Indices: [231, 11]

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
        solution1 = await self.code_generate(instruction="Extract maximum numeric value from a string using regex. Focus on clarity and correctness.")
        solution2 = await self.code_generate(instruction="Use regex to find all numbers in the string, then return the largest one. Prioritize edge case handling.")

        # Optional: Add a third solution using flexible custom for more diversity (e.g., modular approach)
        solution3 = await self.flexible_custom(
            custom_instruction="Break down the problem into helper functions for regex extraction and max finding.",
            generation_pattern="modular",
            strategies=["decompose_problem", "implement_helpers", "combine_solution"]
        )

        # Combine all solutions into an ensemble
        solutions = [solution1, solution2, solution3]

        # Select the best candidate using ScEnsemble
        best_code = await self.sc_ensemble(solutions=solutions)

        # Final verification step: Run the selected code against test cases
        test_result = await self.code_runner(code_to_test=best_code)

        # If the final code fails, attempt to fix it once
        if not test_result.is_correct:
            best_code = await self.code_fix(code=best_code, error_message=test_result.error_message)

        # Return the final verified code
        return best_code