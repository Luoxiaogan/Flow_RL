# Workflow ID: mbpp_20_0
# Benchmark: mbpp
# Data Indices: [101]

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
        It generates multiple diverse solutions, selects the best via ensemble, and verifies with testing.
        """
        # Step 1: Generate two different solutions using varied instructions
        solution1 = await self.code_generate(instruction="Solve using a sorting-based greedy approach.")
        solution2 = await self.code_generate(instruction="Solve using a sliding window technique.")

        # Step 2: Use ScEnsemble to select the best candidate from the two
        solutions = [solution1, solution2]
        best_code = await self.sc_ensemble(solutions=solutions)

        # Step 3: Run final test on the selected solution
        test_result = await self.code_runner(code_to_test=best_code)

        # Step 4: If it fails, attempt to fix it (robustness layer)
        if not test_result.is_correct:
            best_code = await self.code_fix(code=best_code, error_message=test_result.error_message)

        # Step 5: Final verification — optional but adds robustness
        final_test = await self.code_runner(code_to_test=best_code)
        if not final_test.is_correct:
            # If still failing after fixing, fall back to a fresh modular approach
            modular_solution = await self.flexible_custom(
                custom_instruction="Break down into reusable functions",
                generation_pattern="modular",
                strategies=["decompose_problem", "implement_helpers", "combine_solution"]
            )
            best_code = await self.sc_ensemble(solutions=[best_code, modular_solution])

        return best_code