# Workflow ID: mbpp_185_0
# Benchmark: mbpp
# Data Indices: [268]

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
        It uses a two-step generate approach: first outline the solution in natural language, then generate code based on that plan.
        If the generated code fails, it attempts to fix it using the error message.
        """
        # Step 1: Generate a high-level plan (natural language) — this is the core of the "thoughtful generation" requirement
        planning_instruction = (
            "First, analyze the problem thoroughly. Outline the algorithm step-by-step in clear natural language. "
            "Include how to handle edge cases such as empty lists, single-element sublists, or ranges that might be invalid. "
            "Explain how to determine if a sublist is 'outside' the given range and what the output should look like."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual Python code
        code_instruction = (
            "Now, write a Python function that implements the following plan:\n\n"
            f"{plan}\n\n"
            "Ensure the code is efficient, handles all edge cases, and includes comments explaining key steps."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test the fixed version
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, fall back to ensemble-based refinement
                solutions = [
                    initial_code,
                    fixed_code,
                    await self.flexible_custom(
                        custom_instruction="Try solving with a modular approach: break into helper functions",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                    )
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # Step 5: Return the correct code
        return initial_code