# Workflow ID: mbpp_143_0
# Benchmark: mbpp
# Data Indices: [364]

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
            "Outline the algorithm to convert camel case to snake case. "
            "Include steps for handling capital letters, edge cases (empty string, single character, already snake case), "
            "and any assumptions about input format."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a Python function that converts camel case to snake case. "
            "Ensure it handles all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If not correct, attempt to fix based on error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test after fix
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, try a modular approach using FlexibleCustom
                modular_instruction = (
                    "Break down the problem into helper functions: "
                    "one to identify word boundaries, one to join with underscores, "
                    "and one to handle edge cases. Then combine them into the main function."
                )
                modular_code = await self.flexible_custom(
                    custom_instruction=modular_instruction,
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                return modular_code

        # Step 5: If initial code passes, return it
        return initial_code