# Workflow ID: mbpp_191_0
# Benchmark: mbpp
# Data Indices: [285, 116]

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
        # Generate initial solution with clear reasoning
        initial_code = await self.code_generate(instruction="Solve the problem step-by-step, explaining your reasoning clearly in comments.")

        # Test the initial solution
        test_result = await self.code_runner(code_to_test=initial_code)

        # If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed version to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if not retest_result.is_correct:
                # As a fallback, generate one more attempt using flexible custom with a focus on edge cases
                final_code = await self.flexible_custom(
                    custom_instruction="Focus on handling edge cases like empty lists and single-element lists.",
                    strategies=["handle_edge_cases", "analyze_requirements"]
                )
                return final_code
            return fixed_code

        # If initial solution passes, return it
        return initial_code