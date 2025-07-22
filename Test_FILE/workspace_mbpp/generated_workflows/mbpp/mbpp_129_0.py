# Workflow ID: mbpp_129_0
# Benchmark: mbpp
# Data Indices: [125, 85]

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
            "First, outline the algorithm and edge cases in plain English. "
            "Explain how to solve the problem step-by-step, including any assumptions, input validation, and special cases."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Now write the actual Python code that implements this solution. "
            "Include clear comments explaining each part of the implementation."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test after fix
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, try a different approach via flexible custom with modular strategy
                modular_code = await self.flexible_custom(
                    custom_instruction="Implement the solution using a modular approach with helper functions.",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                final_test = await self.code_runner(code_to_test=modular_code)
                if final_test.is_correct:
                    return modular_code
                else:
                    # As last resort, use ensemble of two different approaches
                    alternative_approach = await self.flexible_custom(
                        custom_instruction="Write an alternative solution using a recursive strategy.",
                        generation_pattern="recursive",
                        strategies=["analyze_requirements", "handle_edge_cases"]
                    )
                    solutions = [modular_code, alternative_approach]
                    best_code = await self.sc_ensemble(solutions=solutions)
                    return best_code

        # Step 5: If it passes, return the original code
        return initial_code