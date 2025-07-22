# Workflow ID: mbpp_245_0
# Benchmark: mbpp
# Data Indices: [205]

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
        # Use the FlexibleCustom operator with a modular strategy to build a clean, efficient solution
        # This pattern encourages decomposition and avoids overcomplication — ideal for efficiency
        modular_code = await self.flexible_custom(
            custom_instruction="Break down into reusable functions",
            generation_pattern="modular",
            strategies=["decompose_problem", "implement_helpers", "combine_solution"]
        )
        
        # Test the modular solution
        test_result = await self.code_runner(code_to_test=modular_code)
        
        # If it fails, attempt a fix using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=modular_code,
                error_message=test_result.error_message
            )
            # Run one more test on the fixed version
            final_test = await self.code_runner(code_to_test=fixed_code)
            if final_test.is_correct:
                return fixed_code
            else:
                # As fallback, generate a new simple solution directly
                return await self.code_generate(instruction="Provide a straightforward solution.")
        
        # Return the original modular solution if it passed
        return modular_code