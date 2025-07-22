# Workflow ID: mbpp_159_0
# Benchmark: mbpp
# Data Indices: [366]

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
        # --- Diverse and efficient workflow using Test-Driven pattern with FlexibleCustom ---
        # Using FlexibleCustom with test_driven pattern to build code incrementally based on test feedback
        # This avoids generating a full solution upfront and instead focuses on passing tests step-by-step
        
        code = await self.flexible_custom(
            custom_instruction="Write a function that checks if a string contains all vowels. Focus on passing tests incrementally.",
            generation_pattern="test_driven",
            strategies=["understand_tests", "implement_minimum", "refactor"],
            max_refinements=2  # Allow up to 2 refinements if needed
        )
        
        # Run the generated code against test cases
        test_result = await self.code_runner(code_to_test=code)
        
        # If it fails, attempt one fix using the error message
        if not test_result.is_correct:
            code = await self.code_fix(code=code, error_message=test_result.error_message)
            
            # Re-test after fix
            test_result = await self.code_runner(code_to_test=code)
        
        # Return the final code — either from initial test or post-fix
        return code