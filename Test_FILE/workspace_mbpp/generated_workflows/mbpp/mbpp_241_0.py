# Workflow ID: mbpp_241_0
# Benchmark: mbpp
# Data Indices: [97, 144]

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
        # Use Generate-Test-Fix pattern as instructed
        initial_code = await self.code_generate(instruction="Solve the problem step-by-step, explaining your reasoning clearly in comments.")
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # If the initial solution fails, attempt to fix it using the error message
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            
            # Re-test the fixed code to ensure correctness
            second_test_result = await self.code_runner(code_to_test=fixed_code)
            
            if not second_test_result.is_correct:
                # As a fallback, generate a new solution using a flexible custom approach
                # with strategies focused on understanding requirements and handling edge cases
                final_code = await self.flexible_custom(
                    custom_instruction="Generate a robust solution by analyzing requirements and handling edge cases",
                    strategies=["analyze_requirements", "handle_edge_cases"]
                )
                
                # Final test to confirm correctness
                final_test_result = await self.code_runner(code_to_test=final_code)
                if not final_test_result.is_correct:
                    # Last resort: use ensemble to pick best from multiple attempts
                    solutions = [
                        initial_code,
                        fixed_code,
                        final_code
                    ]
                    return await self.sc_ensemble(solutions=solutions)
                
                return final_code
            
            return fixed_code
        
        return initial_code