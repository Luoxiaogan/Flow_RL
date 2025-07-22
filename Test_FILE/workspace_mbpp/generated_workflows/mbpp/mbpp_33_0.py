# Workflow ID: mbpp_33_0
# Benchmark: mbpp
# Data Indices: [196, 23]

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
        This is a workflow graph for code generation using iterative refinement (Test-Fix loop).
        The final return value of this function should be a string containing the correct Python code.
        """
        # Initial solution generation
        code = await self.code_generate(instruction="Provide a straightforward solution to find the sum of all odd natural numbers in a range.")

        # Iterative refinement loop: test and fix up to 3 times
        for attempt in range(3):
            test_result = await self.code_runner(code_to_test=code)
            if test_result.is_correct:
                return code  # Success! Return the correct code
            
            # If not correct, use the error message to fix the code
            code = await self.code_fix(code=code, error_message=test_result.error_message)
        
        # If we exit the loop without success, return the last generated code (may still be partially correct)
        return code