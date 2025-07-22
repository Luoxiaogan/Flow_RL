# Workflow ID: mbpp_29_0
# Benchmark: mbpp
# Data Indices: [275, 215]

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
        # Use a simple Generate-Test-Fix pattern — efficient and effective for baseline problems
        solution_code = await self.code_generate(instruction="Write a function to compute the LCM of two positive integers. Use the formula: LCM(a,b) = |a*b| / GCD(a,b). Include clear comments.")
        test_result = await self.code_runner(code_to_test=solution_code)
        
        if not test_result.is_correct:
            # If it fails, attempt to fix using the error message
            fixed_code = await self.code_fix(code=solution_code, error_message=test_result.error_message)
            # Re-test the fixed code to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, fall back to a modular approach via FlexibleCustom
                modular_code = await self.flexible_custom(
                    custom_instruction="Break down the problem into helper functions: one for GCD (Euclidean algorithm), another for LCM using GCD.",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                return modular_code
        
        return solution_code