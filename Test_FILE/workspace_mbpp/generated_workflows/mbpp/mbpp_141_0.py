# Workflow ID: mbpp_141_0
# Benchmark: mbpp
# Data Indices: [229]

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
        This is a diverse workflow for code generation that first outlines a plan before coding.
        It uses a two-step reasoning approach: plan → code, then tests and fixes if needed.
        """
        # Step 1: Generate a high-level plan in natural language
        planning_instruction = (
            "Outline the algorithm step-by-step in natural language. "
            "Include how to handle edge cases like negative numbers, zero, and non-numeric inputs. "
            "Explain how rounding up works for different digit positions (e.g., tens, hundreds)."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual Python code
        code_instruction = (
            "Now implement the solution based on this plan: "
            f"{plan}. Ensure the function handles all edge cases described above."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test after fixing
            final_test = await self.code_runner(code_to_test=fixed_code)
            if final_test.is_correct:
                return fixed_code
            else:
                # If still failing, try a fresh start with modular decomposition
                modular_code = await self.flexible_custom(
                    custom_instruction="Break down into reusable helper functions for clarity and correctness.",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                return modular_code

        # If the initial code passes, return it
        return initial_code