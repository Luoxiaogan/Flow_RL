# Workflow ID: mbpp_237_0
# Benchmark: mbpp
# Data Indices: [274]

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
        This is a diverse workflow for code generation that prioritizes thoughtful planning before coding.
        It uses a two-step generation: first a plan, then the actual implementation.
        If the initial code fails, it attempts to fix it. Optionally, if multiple solutions exist, we can ensemble them.
        """
        # Step 1: Generate a high-level plan in natural language
        planning_instruction = (
            "Explain the algorithm step-by-step to solve this problem. "
            "Include how to handle edge cases such as empty tuples, single-element tuples, or negative values."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate the actual code
        code_instruction = (
            "Based on the following plan, write a Python function to solve the problem. "
            "Make sure to handle all edge cases mentioned in the plan. "
            "Use clear comments to explain each part of the solution."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If the code fails, attempt to fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test the fixed code
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # Fallback: Generate a new solution with a different approach
                alternative_plan = await self.code_generate(
                    instruction="Now try solving the same problem using a completely different strategy, e.g., sorting-based or iterative comparison."
                )
                alternative_code = await self.code_generate(
                    instruction=f"Implement the following plan:\n{alternative_plan}"
                )
                # Ensemble both codes (if needed) — but since only one might be correct, we can just use the alternative
                final_code = alternative_code
                return final_code

        # Step 5: If the code passes, return it
        return initial_code