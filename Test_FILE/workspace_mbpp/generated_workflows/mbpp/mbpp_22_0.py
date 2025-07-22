# Workflow ID: mbpp_22_0
# Benchmark: mbpp
# Data Indices: [211]

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
        # Step 1: Generate a high-level plan in natural language (thoughtful design first)
        planning_instruction = (
            "Outline a clear algorithm to solve the problem. "
            "Include steps for handling case sensitivity, multiple occurrences, and edge cases like empty strings or no matches."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a Python function that abbreviates 'road' as 'rd.' in a given string. "
            "Handle all edge cases explicitly. Use clear variable names and comments."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed version
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # As a fallback, try generating again with more precise instruction
                retry_instruction = (
                    "The previous solution failed due to: " + test_result.error_message +
                    ". Rewrite the function from scratch focusing on correctness and edge cases."
                )
                final_code = await self.code_generate(instruction=retry_instruction)
                return final_code
            return fixed_code

        # Step 5: If it passes, return the working code
        return initial_code