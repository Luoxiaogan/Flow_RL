# Workflow ID: mbpp_46_0
# Benchmark: mbpp
# Data Indices: [90]

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
        # Generate initial solution using clear reasoning instruction
        initial_code = await self.code_generate(instruction="Solve the problem step-by-step, explaining your reasoning clearly in comments.")
        
        # Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)
        
        # If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed version to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if not retest_result.is_correct:
                # As a safety net, fallback to a simple iterative refinement loop
                for _ in range(2):  # Allow up to two rounds of fixing
                    fixed_code = await self.code_fix(code=fixed_code, error_message=retest_result.error_message)
                    retest_result = await self.code_runner(code_to_test=fixed_code)
                    if retest_result.is_correct:
                        break
            return fixed_code
        
        # If the first attempt passed, return it
        return initial_code