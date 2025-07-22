# Workflow ID: mbpp_140_0
# Benchmark: mbpp
# Data Indices: [70, 361]

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
        # Generate multiple diverse solutions using different instructions
        solution1 = await self.code_generate(instruction="Solve using bit manipulation techniques with clear comments.")
        solution2 = await self.code_generate(instruction="Solve using iterative approach: check each bit from right to left until unset bit is found.")

        # Optional: Run preliminary tests on both to filter out obviously wrong ones
        test1 = await self.code_runner(code_to_test=solution1)
        test2 = await self.code_runner(code_to_test=solution2)

        # If one is already correct, we can skip ensemble and just return it
        if test1.is_correct:
            return solution1
        if test2.is_correct:
            return solution2

        # Use ScEnsemble to pick the best candidate among the two
        solutions = [solution1, solution2]
        best_code = await self.sc_ensemble(solutions=solutions)

        # Final verification step: run the selected code through the runner
        final_test = await self.code_runner(code_to_test=best_code)
        if not final_test.is_correct:
            # If even the best fails, attempt to fix based on error message
            best_code = await self.code_fix(
                code=best_code,
                error_message=final_test.error_message
            )
            # One last test after fixing
            final_test = await self.code_runner(code_to_test=best_code)
            if not final_test.is_correct:
                # As fallback, try a flexible custom strategy (e.g., modular or recursive)
                fallback_code = await self.flexible_custom(
                    custom_instruction="Try solving by breaking into helper functions",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "handle_edge_cases"]
                )
                final_test = await self.code_runner(code_to_test=fallback_code)
                if final_test.is_correct:
                    return fallback_code
                else:
                    # Last resort: use test-driven approach to build incrementally
                    test_driven_code = await self.flexible_custom(
                        custom_instruction="Start with minimal implementation that passes basic test cases.",
                        generation_pattern="test_driven",
                        strategies=["understand_tests", "implement_minimum"]
                    )
                    return test_driven_code

        return best_code