# Workflow ID: mbpp_152_0
# Benchmark: mbpp
# Data Indices: [100, 123]

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
        Generates multiple diverse solutions, selects the best via ScEnsemble, and verifies with CodeRunner.
        """
        # Step 1: Generate two different solutions using varied instructions to encourage diversity
        solution1 = await self.code_generate(instruction="Solve using a single-pass approach with running sums.")
        solution2 = await self.code_generate(instruction="Solve by calculating left and right sums separately for each index.")

        # Step 2: Use ScEnsemble to select the best candidate from the two solutions
        solutions = [solution1, solution2]
        best_code = await self.sc_ensemble(solutions=solutions)

        # Step 3: Run final test on the selected solution to ensure correctness
        test_result = await self.code_runner(code_to_test=best_code)
        
        # If the ensemble-selected code fails, attempt to fix it using the error message
        if not test_result.is_correct:
            best_code = await self.code_fix(code=best_code, error_message=test_result.error_message)

        # Final verification step — even after fixing, re-run to confirm correctness
        final_test = await self.code_runner(code_to_test=best_code)
        if not final_test.is_correct:
            # Fallback: generate one more solution using a modular strategy as last resort
            fallback_code = await self.flexible_custom(
                custom_instruction="Break down into reusable helper functions",
                generation_pattern="modular",
                strategies=["decompose_problem", "implement_helpers", "combine_solution"]
            )
            return fallback_code

        return best_code