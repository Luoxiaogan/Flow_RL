# Workflow ID: mbpp_144_0
# Benchmark: mbpp
# Data Indices: [188, 221]

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
        # Use Generate-Test-Fix pattern as instructed: first generate, then test, then fix if needed
        initial_code = await self.code_generate(instruction="Write a function to calculate the perimeter of a regular polygon. Include clear comments explaining each step.")
        
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # If it fails, use the error message to guide a fix
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Run one more test on the fixed code to ensure correctness
            post_fix_test = await self.code_runner(code_to_test=fixed_code)
            if not post_fix_test.is_correct:
                # In rare cases, even one fix might not be enough — but per task instructions, we stop after one fix
                pass  # For now, just return the fixed version; real-world systems might loop or escalate
            return fixed_code
        
        # If the initial code passes all tests, return it directly
        return initial_code