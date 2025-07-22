# Workflow ID: mbpp_78_0
# Benchmark: mbpp
# Data Indices: [259, 55]

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
        # Initial code generation using a clear instruction
        code = await self.code_generate(instruction="Write a Python function to check if a string ends with only alphanumeric characters using regex. Include comments explaining each step.")
        
        # Iterative refinement loop: 3 iterations max
        for attempt in range(3):
            test_result = await self.code_runner(code_to_test=code)
            
            if test_result.is_correct:
                # Success! Return the working solution
                return code
            
            # If failed, use the error message to fix the code
            code = await self.code_fix(code=code, error_message=test_result.error_message)
        
        # If we exit the loop without success, return the last generated code (may still fail)
        return code