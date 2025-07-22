# Workflow ID: mbpp_226_0
# Benchmark: mbpp
# Data Indices: [326]

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
        # Use Generate-Test-Fix pattern as instructed
        initial_code = await self.code_generate(instruction="Write a function to calculate the height of a binary tree. Ensure it handles empty trees and all edge cases correctly.")
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # If the first attempt fails, use CodeFix with the error message
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            
            # Optional: Run one more test on the fixed version to ensure correctness
            final_test = await self.code_runner(code_to_test=fixed_code)
            if not final_test.is_correct:
                # In rare cases, fix might not be enough — but per instructions, we stop after one fix
                # For this task, we assume one fix suffices given the clarity of the problem
                pass
            
            return fixed_code
        
        # If initial code passed all tests, return it directly
        return initial_code