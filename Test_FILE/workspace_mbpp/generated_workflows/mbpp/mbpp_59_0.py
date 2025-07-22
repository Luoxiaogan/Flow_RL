# Workflow ID: mbpp_59_0
# Benchmark: mbpp
# Data Indices: [102]

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
        # --- Diverse and Correctness-Focused Generate-Test-Fix Pattern ---
        initial_code = await self.code_generate(instruction="Write a function to check if a key exists in a dictionary. Be explicit about edge cases like empty dictionaries or non-existent keys.")
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # Use CodeFix to resolve the issue based on the error message
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            
            # Re-test the fixed code to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            
            if not retest_result.is_correct:
                # If still failing, use FlexibleCustom with a more structured approach
                refined_code = await self.flexible_custom(
                    custom_instruction="Rebuild solution focusing on edge case handling and clear logic.",
                    previous_results=[fixed_code]
                )
                
                # Final test to guarantee correctness
                final_result = await self.code_runner(code_to_test=refined_code)
                if not final_result.is_correct:
                    # As a last resort, fallback to ensemble of two different approaches
                    approach1 = await self.code_generate(instruction="Solve using direct 'in' operator.")
                    approach2 = await self.code_generate(instruction="Solve using dict.get() method with default value.")
                    solutions = [approach1, approach2]
                    final_code = await self.sc_ensemble(solutions=solutions)
                    return final_code
                
                return refined_code
            
            return fixed_code
        
        return initial_code