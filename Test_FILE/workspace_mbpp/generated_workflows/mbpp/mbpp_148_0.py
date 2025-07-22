# Workflow ID: mbpp_148_0
# Benchmark: mbpp
# Data Indices: [280]

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
        # --- Diverse Parallel Ensemble & Test Pattern ---
        
        # Generate two different solutions using varied instructions to promote diversity
        solution1 = await self.code_generate(instruction="Solve by iterating through the list once and tracking first even and odd numbers.")
        solution2 = await self.code_generate(instruction="Solve by filtering evens and odds separately, then taking the first from each.")

        # Use ScEnsemble to select the best among them (based on internal heuristics or test results)
        candidate_solutions = [solution1, solution2]
        best_code = await self.sc_ensemble(solutions=candidate_solutions)

        # Final verification: Run the selected code against test cases
        test_result = await self.code_runner(code_to_test=best_code)
        
        # If the ensemble-selected code fails, fall back to iterative refinement
        if not test_result.is_correct:
            # Attempt one fix based on error message
            fixed_code = await self.code_fix(code=best_code, error_message=test_result.error_message)
            # Re-test the fixed version
            final_test = await self.code_runner(code_to_test=fixed_code)
            if final_test.is_correct:
                return fixed_code
            else:
                # As a last resort, generate a new solution using a flexible custom approach
                # with strategies focused on correctness and edge-case handling
                fallback_code = await self.flexible_custom(
                    custom_instruction="Write a robust solution that handles empty lists, single elements, and mixed parity.",
                    previous_results=[best_code, fixed_code],
                    generation_pattern="incremental",
                    strategies=["analyze_requirements", "handle_edge_cases", "optimize_solution"],
                    max_refinements=1
                )
                return fallback_code

        # Return the verified correct solution
        return best_code