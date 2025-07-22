# Workflow ID: mbpp_49_0
# Benchmark: mbpp
# Data Indices: [77, 303]

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
        # Generate initial solution
        initial_code = await self.code_generate(instruction="Write a Python function that removes all spaces from a given string.")

        # Run test to check correctness
        test_result = await self.code_runner(code_to_test=initial_code)

        # If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed code to ensure it works
            final_test = await self.code_runner(code_to_test=fixed_code)
            if final_test.is_correct:
                return fixed_code
            else:
                # In rare cases, even after fixing, it might fail — fallback to a second attempt
                # This ensures robustness in case the first fix was incomplete
                return await self.code_generate(instruction="Based on the previous failure, write a corrected version of the space-removal function.")
        
        # If initial code passed, return it
        return initial_code