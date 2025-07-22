# Workflow ID: mbpp_229_0
# Benchmark: mbpp
# Data Indices: [137, 4]

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
        # Use a simple Generate-Test-Fix pattern — efficient and effective for baseline problems
        solution_code = await self.code_generate(instruction="Provide a straightforward solution.")
        test_result = await self.code_runner(code_to_test=solution_code)
        
        if not test_result.is_correct:
            # If it fails, attempt to fix using error message
            solution_code = await self.code_fix(code=solution_code, error_message=test_result.error_message)
            
            # Run one more test after fixing
            test_result = await self.code_runner(code_to_test=solution_code)
            
            # If still failing, fall back to ensemble of two different approaches
            if not test_result.is_correct:
                # Generate two distinct solutions: iterative and recursive (or other strategies)
                iterative_solution = await self.flexible_custom(
                    custom_instruction="Implement iteratively",
                    generation_pattern="incremental",
                    strategies=["analyze_requirements", "handle_edge_cases"]
                )
                recursive_solution = await self.flexible_custom(
                    custom_instruction="Implement recursively",
                    generation_pattern="recursive",
                    strategies=["decompose_problem", "base_case_handling"]
                )
                
                # Ensemble selects best among them
                solution_code = await self.sc_ensemble(solutions=[solution_code, iterative_solution, recursive_solution])
                
                # Final test to ensure correctness
                final_test = await self.code_runner(code_to_test=solution_code)
                if not final_test.is_correct:
                    # Last resort: use flexible_custom with test-driven strategy
                    solution_code = await self.flexible_custom(
                        custom_instruction="Write code that passes all tests step by step.",
                        generation_pattern="test_driven",
                        strategies=["understand_tests", "implement_minimum", "refactor"]
                    )

        return solution_code