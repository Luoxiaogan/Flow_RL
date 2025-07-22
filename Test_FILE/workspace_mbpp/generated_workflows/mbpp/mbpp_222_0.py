# Workflow ID: mbpp_222_0
# Benchmark: mbpp
# Data Indices: [312]

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
        This is a workflow graph for code generation using iterative refinement (Test-Fix loop).
        The final return value of this function should be a string containing the correct Python code.
        """
        # Step 1: Generate initial solution
        code = await self.code_generate(instruction="Write a function that checks if a string ends with a number.")
        
        # Step 2: Iterative refinement loop (2-3 times)
        for attempt in range(2):  # Loop 2 times for refinement
            test_result = await self.code_runner(code_to_test=code)
            
            if test_result.is_correct:
                # Success! Return the correct code
                return code
            
            # If failed, fix the code using error message
            code = await self.code_fix(code=code, error_message=test_result.error_message)
        
        # Final check after loop
        final_test = await self.code_runner(code_to_test=code)
        if not final_test.is_correct:
            # As a fallback, generate one more fix attempt with a fresh instruction
            code = await self.code_generate(
                instruction="Rewrite the function to correctly detect numbers at the end of a string. Focus on edge cases like empty strings or non-numeric suffixes."
            )
            # One last test
            final_test = await self.code_runner(code_to_test=code)
            if not final_test.is_correct:
                # If still failing, use flexible custom with test-driven strategy as last resort
                code = await self.flexible_custom(
                    custom_instruction="Implement a test-driven approach to ensure correctness.",
                    generation_pattern="test_driven",
                    strategies=["understand_tests", "implement_minimum", "refactor"],
                    max_refinements=1
                )
        
        return code