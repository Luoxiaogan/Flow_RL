# Workflow ID: mbpp_180_0
# Benchmark: mbpp
# Data Indices: [86]

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
        # Parallel Ensemble & Test Pattern: Generate multiple solutions with varied instructions
        solutions = [
            await self.code_generate(instruction="Implement GCD using recursion. Focus on clarity and correctness.")
            ,
            await self.code_generate(instruction="Solve GCD recursively. Handle edge cases like negative numbers and zero explicitly.")
        ]

        # Use ScEnsemble to select the best candidate from the generated solutions
        best_code = await self.sc_ensemble(solutions=solutions)

        # Optional: Run a final test to ensure robustness (even if ensemble is strong)
        test_result = await self.code_runner(code_to_test=best_code)
        
        # If the selected solution fails, attempt to fix it using CodeFix
        if not test_result.is_correct:
            best_code = await self.code_fix(code=best_code, error_message=test_result.error_message)

        return best_code