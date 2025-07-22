# Workflow ID: mbpp_81_0
# Benchmark: mbpp
# Data Indices: [143, 338]

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
        # Step 1: Generate a high-level plan in natural language (not code yet)
        planning_instruction = (
            "Outline the algorithm step-by-step in natural language. "
            "Include how to handle edge cases such as empty inputs, mixed types, or nested structures. "
            "Explain what constitutes a 'none value' and how to check for it efficiently."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_generation_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a complete, correct Python function that solves the problem. "
            "Ensure the code includes clear comments explaining each step and handles all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_generation_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test after fixing
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # Fallback: Try ensemble with original + fixed version
                solutions = [initial_code, fixed_code]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # Step 5: If it passes, return the initial code
        return initial_code