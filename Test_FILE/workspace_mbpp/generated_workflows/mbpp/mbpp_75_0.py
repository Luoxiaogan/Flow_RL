# Workflow ID: mbpp_75_0
# Benchmark: mbpp
# Data Indices: [35]

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
        # Generate initial solution using a clear instruction to encourage correctness
        solution_code = await self.code_generate(instruction="Write a Python function that checks if the roots of a quadratic equation are reciprocal. Include clear comments explaining how you use the relationship between coefficients and roots.")

        # Run tests to check correctness
        test_result = await self.code_runner(code_to_test=solution_code)

        # If the code fails, fix it based on the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=solution_code, error_message=test_result.error_message)
            # Re-test the fixed code to ensure the issue is resolved
            post_fix_test = await self.code_runner(code_to_test=fixed_code)
            if not post_fix_test.is_correct:
                # If still failing, we might need more iterations or a different strategy
                # For now, return the fixed version as our best effort
                return fixed_code
            else:
                return fixed_code
        else:
            # If the initial code passed all tests, return it directly
            return solution_code