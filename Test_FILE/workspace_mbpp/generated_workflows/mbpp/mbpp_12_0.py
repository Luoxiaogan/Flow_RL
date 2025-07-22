# Workflow ID: mbpp_12_0
# Benchmark: mbpp
# Data Indices: [42, 195]

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
        # --- Diverse and Efficient Workflow: Generate-Test-Fix Pattern with One Fix Attempt ---
        initial_code = await self.code_generate(instruction="Write a function that matches a word containing 'z', not at the start or end of the word. Include clear comments explaining each step.")
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # If the initial solution fails, attempt one fix using error message
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Re-test the fixed code to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # Fallback: use ensemble to pick from multiple attempts
                solutions = [
                    initial_code,
                    fixed_code,
                    await self.code_generate(instruction="Try solving it again with a different approach.")
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code
        
        # If initial code passed all tests, return it
        return initial_code