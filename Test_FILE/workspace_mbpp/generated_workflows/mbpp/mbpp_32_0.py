# Workflow ID: mbpp_32_0
# Benchmark: mbpp
# Data Indices: [332]

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
        This is a diverse workflow for code generation that first plans, then codes.
        Uses a two-step Generate-Test-Fix structure with explicit planning phase.
        """
        # Step 1: Generate a detailed plan in natural language
        planning_instruction = (
            "Outline the algorithm to convert camel case to snake case using regex. "
            "Include steps for identifying word boundaries, handling edge cases (like consecutive uppercase letters), "
            "and explain how you would implement it in Python with clear comments."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Write a complete Python function that uses regex to convert camel case to snake case. "
            "Ensure the solution handles all edge cases mentioned in the plan. "
            "Use clear, readable code with comments explaining each part."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
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
                # If still failing, try ensemble approach with multiple variations
                # Generate alternative approaches based on the same plan
                alternative1 = await self.code_generate(
                    instruction="Implement the conversion using a different regex pattern or logic from the plan."
                )
                alternative2 = await self.code_generate(
                    instruction="Re-implement the solution focusing on clarity and edge case handling, as per the plan."
                )
                solutions = [fixed_code, alternative1, alternative2]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # If initial code passed, return it
        return initial_code