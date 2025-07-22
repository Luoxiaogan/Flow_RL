# Workflow ID: mbpp_211_0
# Benchmark: mbpp
# Data Indices: [84]

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
        # Step 1: Generate a high-level plan in natural language
        planning_instruction = (
            "First, outline the algorithm step-by-step in plain English. "
            "Include how to identify prime numbers, how to sum them efficiently, "
            "and discuss edge cases like n=0, n=1, or small values. "
            "Be thorough but concise."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use that plan to generate actual code
        code_instruction = (
            "Now implement the solution based on this plan: "
            f"{plan}. Ensure the code is efficient and handles all edge cases mentioned."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Run tests to validate the implementation
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Re-test after fixing
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, use flexible custom with test-driven strategy
                flexible_code = await self.flexible_custom(
                    custom_instruction="Use a test-driven approach to build the solution incrementally.",
                    generation_pattern="test_driven",
                    strategies=["understand_tests", "implement_minimum", "refactor"]
                )
                return flexible_code

        # Step 5: If successful, return the original code
        return initial_code