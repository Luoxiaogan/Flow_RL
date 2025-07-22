# Workflow ID: mbpp_53_0
# Benchmark: mbpp
# Data Indices: [156, 228]

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
            "Include how to handle edge cases such as empty lists, duplicates, or single elements. "
            "Then, describe how you would translate this plan into efficient Python code."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Using the following plan:\n{plan}\n"
            "Now write a complete and correct Python function that solves the problem. "
            "Include clear comments explaining each part of the logic. "
            "Handle all edge cases explicitly."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Run the test suite
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Re-test the fixed code
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # Fallback: Try a different approach via flexible custom
                fallback_code = await self.flexible_custom(
                    custom_instruction="Use a modular approach to solve the problem",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                # Final test of fallback
                final_result = await self.code_runner(code_to_test=fallback_code)
                if final_result.is_correct:
                    return fallback_code
                else:
                    # As last resort, use ensemble of two approaches
                    solutions = [
                        fixed_code,
                        fallback_code
                    ]
                    best_code = await self.sc_ensemble(solutions=solutions)
                    return best_code

        # If initial code passed, return it
        return initial_code