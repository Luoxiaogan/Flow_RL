# Workflow ID: mbpp_195_0
# Benchmark: mbpp
# Data Indices: [365]

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
        # Parallel Ensemble & Test Pattern: Generate multiple solutions with varied instructions
        solution1 = await self.code_generate(instruction="Remove empty tuples using list comprehension.")
        solution2 = await self.code_generate(instruction="Remove empty tuples by filtering with a loop and condition.")

        # Use ScEnsemble to select the best among the two
        best_code = await self.sc_ensemble(solutions=[solution1, solution2])

        # Optional: Run final test to ensure correctness (robustness check)
        test_result = await self.code_runner(code_to_test=best_code)
        if not test_result.is_correct:
            # If ensemble fails, fall back to iterative refinement using flexible_custom
            refined_code = await self.flexible_custom(
                custom_instruction="Refine the selected solution based on error",
                previous_results=[best_code],
                generation_pattern="incremental",
                strategies=["handle_edge_cases"],
                max_refinements=1
            )
            # Final verification
            final_test = await self.code_runner(code_to_test=refined_code)
            if not final_test.is_correct:
                # Last resort: fix based on error message
                best_code = await self.code_fix(
                    code=refined_code,
                    error_message=final_test.error_message
                )
            else:
                best_code = refined_code

        return best_code