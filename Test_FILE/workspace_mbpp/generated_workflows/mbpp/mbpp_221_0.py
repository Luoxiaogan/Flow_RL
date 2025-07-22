# Workflow ID: mbpp_221_0
# Benchmark: mbpp
# Data Indices: [356]

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
        # Parallel Ensemble & Test pattern: Generate multiple diverse solutions
        solution1 = await self.code_generate(instruction="Solve using bit manipulation with bitwise AND and subtraction.")
        solution2 = await self.code_generate(instruction="Solve by iterating through bits from right to left until first set bit is found.")

        # Evaluate both solutions using ScEnsemble to pick the best one
        solutions = [solution1, solution2]
        best_code = await self.sc_ensemble(solutions=solutions)

        # Final verification step: Run the selected code against test cases
        test_result = await self.code_runner(code_to_test=best_code)
        
        # If the ensemble result fails, fall back to iterative refinement
        if not test_result.is_correct:
            # Attempt to fix the code based on error message
            fixed_code = await self.code_fix(code=best_code, error_message=test_result.error_message)
            # Re-run the fixed code
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # If still failing, generate a new solution using flexible custom with modular strategy
                new_solution = await self.flexible_custom(
                    custom_instruction="Break down the problem into helper functions: isolate rightmost set bit, count positions.",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                # Test the new modular solution
                test_result = await self.code_runner(code_to_test=new_solution)
                if test_result.is_correct:
                    return new_solution
                else:
                    # As last resort, try an incremental approach
                    incremental_code = await self.flexible_custom(
                        custom_instruction="Build solution incrementally: handle base case, then general case.",
                        generation_pattern="incremental",
                        strategies=["analyze_requirements", "handle_edge_cases"]
                    )
                    return incremental_code
            return fixed_code
        
        return best_code