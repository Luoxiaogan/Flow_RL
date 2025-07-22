# Workflow ID: mbpp_100_0
# Benchmark: mbpp
# Data Indices: [88, 147]

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
        This is a diverse workflow graph for code generation.
        It first generates a high-level plan, then uses that to write the actual code.
        If the code fails, it attempts to fix it. If still failing, it tries an ensemble of alternatives.
        """
        # Step 1: Generate a detailed plan in natural language
        plan_instruction = (
            "Outline the algorithm, key steps, and edge cases for solving this problem. "
            "Do not write code yet—focus on strategy and reasoning."
        )
        plan = await self.code_generate(instruction=plan_instruction)

        # Step 2: Use the plan to generate the actual code
        code_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Write a Python function that solves the problem. "
            "Include clear comments explaining each major step."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)
        if test_result.is_correct:
            return initial_code

        # Step 4: Attempt to fix based on error
        fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
        test_result = await self.code_runner(code_to_test=fixed_code)
        if test_result.is_correct:
            return fixed_code

        # Step 5: Try a modular approach using FlexibleCustom
        modular_code = await self.flexible_custom(
            custom_instruction="Break down the solution into helper functions for clarity and correctness.",
            generation_pattern="modular",
            strategies=["decompose_problem", "implement_helpers", "combine_solution"]
        )

        # Step 6: Ensemble: compare original, fixed, and modular versions
        solutions = [initial_code, fixed_code, modular_code]
        best_code = await self.sc_ensemble(solutions=solutions)

        # Final test of the best candidate
        final_test = await self.code_runner(code_to_test=best_code)
        if final_test.is_correct:
            return best_code

        # Fallback: use test-driven approach with flexible custom
        test_driven_code = await self.flexible_custom(
            custom_instruction="Start with minimal implementation to pass tests, then refine.",
            generation_pattern="test_driven",
            strategies=["understand_tests", "implement_minimum", "refactor"],
            max_refinements=2
        )

        return test_driven_code