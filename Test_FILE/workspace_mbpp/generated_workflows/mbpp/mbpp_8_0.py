# Workflow ID: mbpp_8_0
# Benchmark: mbpp
# Data Indices: [165]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
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
            "Outline the algorithm to iterate over all pairs of consecutive items in a list. "
            "Include edge cases (empty list, single item, two items) and explain how you would implement it in Python."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Write a Python function that iterates over all pairs of consecutive items in a list. "
            "Handle edge cases explicitly. Return a list of tuples where each tuple contains a pair of consecutive elements."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If not correct, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test the fixed version
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, try one more time with a different strategy
                fallback_code = await self.flexible_custom(
                    custom_instruction="Use a modular approach: break into helper functions.",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                return fallback_code

        # Step 5: If correct, return the original code
        return initial_code