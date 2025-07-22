# Workflow ID: mbpp_147_0
# Benchmark: mbpp
# Data Indices: [297, 342]

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
            "First, analyze the problem requirements and outline a clear algorithm "
            "in natural language. Include steps for handling edge cases like empty lists, "
            "negative or zero elements to extract, or invalid inputs."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_generation_instruction = (
            "Now, write a Python function based on this plan: " + plan +
            ". Ensure it handles all edge cases explicitly and includes clear comments."
        )
        initial_code = await self.code_generate(instruction=code_generation_instruction)

        # Step 3: Test the initial code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If not correct, attempt to fix it using error feedback
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Re-test after fix
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, use iterative refinement (Test-Fix Loop)
                for _ in range(2):  # Max 2 refinements
                    fixed_code = await self.code_fix(
                        code=fixed_code,
                        error_message=retest_result.error_message
                    )
                    retest_result = await self.code_runner(code_to_test=fixed_code)
                    if retest_result.is_correct:
                        return fixed_code
                # If after 2 fixes it still fails, fall back to ensemble approach
                # Generate one more alternative solution
                alternative_solution = await self.code_generate(
                    instruction="Provide an alternative implementation that addresses potential issues from previous failures."
                )
                solutions = [fixed_code, alternative_solution]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # Step 5: If initial code passed, return it
        return initial_code