# Workflow ID: mbpp_176_0
# Benchmark: mbpp
# Data Indices: [324]

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
        This is a diverse workflow graph for code generation that emphasizes thoughtful planning before coding.
        It first generates a natural language plan, then uses that to write the actual code.
        If the code fails, it attempts to fix it using the error message.
        """
        # Step 1: Generate a detailed plan in natural language
        plan_instruction = (
            "First, outline a step-by-step algorithm to solve this problem. "
            "Include how you will handle edge cases like empty tuples or single-element tuples. "
            "Explain your approach clearly in plain English."
        )
        planning_code = await self.code_generate(instruction=plan_instruction)

        # Step 2: Use the plan to generate the actual Python function
        code_instruction = (
            "Now, implement the solution based on this plan: "
            f"{planning_code}. "
            "Write a clean, efficient Python function that computes the product of all numbers in a tuple."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If not correct, attempt to fix it
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Re-test the fixed version
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, use ensemble to try multiple approaches
                solutions = [
                    await self.code_generate(instruction="Solve using a simple loop."),
                    await self.code_generate(instruction="Solve using recursion."),
                    await self.code_generate(instruction="Solve using functools.reduce.")
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                final_test = await self.code_runner(code_to_test=best_code)
                if final_test.is_correct:
                    return best_code
                else:
                    # Fallback: use flexible custom with modular strategy
                    modular_code = await self.flexible_custom(
                        custom_instruction="Break down into helper functions and combine.",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                    )
                    return modular_code

        # Step 5: Return the original or fixed code if correct
        return initial_code