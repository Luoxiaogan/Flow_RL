# Workflow ID: mbpp_99_0
# Benchmark: mbpp
# Data Indices: [202, 173]

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
        # Step 1: Generate two different code solutions using varied instructions
        solution1 = await self.code_generate(instruction="Write a function to check if a number is a perfect square using integer arithmetic and binary search.")
        solution2 = await self.code_generate(instruction="Write a function to check if a number is a perfect square using math.sqrt() and rounding checks.")

        # Step 2: Use ScEnsemble to select the best candidate from the two
        solutions = [solution1, solution2]
        best_code = await self.sc_ensemble(solutions=solutions)

        # Step 3: Run the final selected code through the test runner to verify correctness
        test_result = await self.code_runner(code_to_test=best_code)

        # If it fails, attempt a fix based on the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=best_code, error_message=test_result.error_message)
            # Re-test the fixed version
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # Fallback: generate a new solution using flexible custom with modular strategy
                fallback_code = await self.flexible_custom(
                    custom_instruction="Solve the problem by breaking it into helper functions for clarity and correctness.",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "handle_edge_cases"]
                )
                return fallback_code
            return fixed_code

        # Return the verified correct code
        return best_code