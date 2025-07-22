# Workflow ID: mbpp_0_0
# Benchmark: mbpp
# Data Indices: [16]

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
        # Diverse and efficient workflow: Use FlexibleCustom with "incremental" pattern to build a robust solution step-by-step
        # This avoids premature optimization while ensuring clarity and correctness through structured refinement.
        initial_code = await self.flexible_custom(
            custom_instruction="Build the solution incrementally, focusing on understanding the problem and handling edge cases.",
            generation_pattern="incremental",
            strategies=["analyze_requirements", "handle_edge_cases", "optimize_solution"],
            max_refinements=1,
            use_structured_output=True
        )
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # If it fails, attempt a fix using the error message — crucial for iterative improvement
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: retest the fixed version to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, fall back to a simple ensemble of two approaches (e.g., recursive vs iterative)
                alternative_solutions = [
                    await self.code_generate(instruction="Solve using a mathematical approach based on GCD."),
                    await self.code_generate(instruction="Solve using a brute-force simulation approach.")
                ]
                best_code = await self.sc_ensemble(solutions=alternative_solutions)
                return best_code
        
        return initial_code