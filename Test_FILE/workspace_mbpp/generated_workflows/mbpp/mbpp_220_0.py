# Workflow ID: mbpp_220_0
# Benchmark: mbpp
# Data Indices: [249]

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
        It uses a two-step generation approach: first outline the plan in natural language, then generate code based on that plan.
        If the generated code fails, it attempts to fix it using error feedback.
        """
        # Step 1: Generate a detailed plan in natural language
        planning_instruction = (
            "First, analyze the problem requirements. Then, describe the algorithm step-by-step "
            "in clear natural language, including edge cases (e.g., negative angles, sum not equal to 180, zero area). "
            "Explain how to validate triangle validity using angle constraints."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a Python function that checks if a triangle of positive area is possible given three angles. "
            "Ensure the code handles all edge cases mentioned in the plan and includes clear comments."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using the error message
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
                # If still failing, fall back to ensemble with multiple strategies
                solutions = [
                    await self.code_generate(instruction="Solve using a direct logical check for valid triangle angles."),
                    await self.code_generate(instruction="Solve by validating angle sum and positivity separately."),
                    await self.code_generate(instruction="Solve using helper functions for clarity.")
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # Step 5: If the initial code passed, return it
        return initial_code