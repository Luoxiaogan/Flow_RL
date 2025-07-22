# Workflow ID: mbpp_240_0
# Benchmark: mbpp
# Data Indices: [132]

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
        # --- Diverse Iterative Refinement Workflow ---
        # Start with an initial solution using a clear instruction
        code = await self.code_generate(instruction="Write a Python function to find the index of the first occurrence of a target number in a sorted array. Use binary search for efficiency.")

        # Loop 2-3 times to refine the solution iteratively
        for attempt in range(3):  # Max 3 refinement attempts
            test_result = await self.code_runner(code_to_test=code)
            
            if test_result.is_correct:
                # Success! Return the working code
                return code
            
            # If it fails, use CodeFix to repair based on the error message
            code = await self.code_fix(code=code, error_message=test_result.error_message)

        # If we exit the loop without success, return the last generated code (even if it's incorrect)
        return code