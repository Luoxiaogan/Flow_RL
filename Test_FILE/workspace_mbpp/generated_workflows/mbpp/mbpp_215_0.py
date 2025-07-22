# Workflow ID: mbpp_215_0
# Benchmark: mbpp
# Data Indices: [180]

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
        This is a diverse workflow for code generation that emphasizes thoughtful planning before coding.
        First, it generates a detailed plan in natural language, then uses that to write the actual code.
        If the generated code fails, it attempts to fix it. Optionally, it can fall back to ensemble if needed.
        """
        # Step 1: Generate a high-level plan (natural language outline of algorithm and edge cases)
        planning_instruction = (
            "Outline the algorithm to determine if the count of divisors is even or odd. "
            "Include steps for handling edge cases like 0, 1, and perfect squares. "
            "Explain how you would translate this into Python code."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            "Based on the following plan:\n"
            f"{plan}\n\n"
            "Write a Python function that returns 'even' if the number of divisors is even, otherwise 'odd'. "
            "Ensure it handles all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Re-test the fixed version
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # If still failing, try an alternative approach via flexible custom with modular strategy
                modular_code = await self.flexible_custom(
                    custom_instruction="Break down the divisor counting logic into reusable helper functions.",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                # Ensemble: compare original fixed code vs modular approach
                solutions = [fixed_code, modular_code]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # If successful, return the tested code
        return initial_code