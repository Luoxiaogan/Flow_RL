# Workflow ID: mbpp_61_0
# Benchmark: mbpp
# Data Indices: [71]

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
        # Use the FlexibleCustom operator with a modular strategy to decompose and build a robust solution
        modular_code = await self.flexible_custom(
            custom_instruction="Break down into reusable functions",
            generation_pattern="modular",
            strategies=["decompose_problem", "implement_helpers", "combine_solution"]
        )
        
        # Run the test to validate the modular approach
        test_result = await self.code_runner(code_to_test=modular_code)
        
        # If it fails, attempt a fix using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=modular_code, error_message=test_result.error_message)
            # Re-test the fixed version
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # Fallback: Generate a new simple solution directly
                fallback_code = await self.code_generate(instruction="Provide a straightforward solution that uses max() or basic comparisons.")
                return fallback_code
            return fixed_code
        
        # If the modular solution passes, return it
        return modular_code