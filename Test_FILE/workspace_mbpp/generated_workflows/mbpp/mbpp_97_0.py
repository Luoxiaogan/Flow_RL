# Workflow ID: mbpp_97_0
# Benchmark: mbpp
# Data Indices: [164]

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
        # Use a simple Generate-Test-Fix pattern to ensure correctness with minimal overhead
        # This is efficient and avoids unnecessary complexity while still being robust
        
        solution_code = await self.code_generate(instruction="Provide a straightforward solution that efficiently finds the nth polite number. Explain your approach in comments.")
        test_result = await self.code_runner(code_to_test=solution_code)
        
        if not test_result.is_correct:
            # If the initial solution fails, attempt one fix using error feedback
            solution_code = await self.code_fix(code=solution_code, error_message=test_result.error_message)
            
            # Re-test after fixing
            test_result = await self.code_runner(code_to_test=solution_code)
            
            # If it still fails, fall back to an ensemble of two different approaches
            if not test_result.is_correct:
                # Generate two distinct solutions: one based on direct computation, another on iterative checking
                sol1 = await self.code_generate(instruction="Solve using mathematical properties of polite numbers (e.g., numbers that are not powers of 2).")
                sol2 = await self.code_generate(instruction="Solve by iterating through natural numbers and checking if each is polite.")
                
                # Select the best performing one via ensemble
                solution_code = await self.sc_ensemble(solutions=[sol1, sol2])
                
                # Final test
                test_result = await self.code_runner(code_to_test=solution_code)
                
                # If ensemble also fails, try one last refinement using flexible custom with modular strategy
                if not test_result.is_correct:
                    solution_code = await self.flexible_custom(
                        custom_instruction="Break down into reusable helper functions to check if a number is polite.",
                        strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                    )

        return solution_code