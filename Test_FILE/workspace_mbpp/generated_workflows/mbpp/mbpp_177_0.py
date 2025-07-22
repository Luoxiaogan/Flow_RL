# Workflow ID: mbpp_177_0
# Benchmark: mbpp
# Data Indices: [319, 136]

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
            "Outline the algorithm, key steps, and edge cases for solving this problem. "
            "Do not write code yet—focus on clarity and completeness."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a Python function that solves the problem correctly. "
            "Include comments explaining each major step. Handle all edge cases explicitly."
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
                # If still failing, try an ensemble approach with multiple strategies
                solutions = [
                    await self.code_generate(instruction="Solve using a list comprehension approach."),
                    await self.code_generate(instruction="Solve using filter() and lambda."),
                    await self.code_generate(instruction="Solve using a loop with explicit condition checks.")
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                final_test = await self.code_runner(code_to_test=best_code)
                if final_test.is_correct:
                    return best_code
                else:
                    # As fallback: use flexible custom with modular strategy
                    flexible_code = await self.flexible_custom(
                        custom_instruction="Break down into reusable functions",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                    )
                    return flexible_code

        # Step 5: Return the working solution
        return initial_code