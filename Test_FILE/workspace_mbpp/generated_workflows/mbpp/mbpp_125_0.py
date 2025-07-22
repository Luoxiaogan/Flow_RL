# Workflow ID: mbpp_125_0
# Benchmark: mbpp
# Data Indices: [337]

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
        # Use Generate-Test-Fix pattern as specified
        solution_code = await self.code_generate(instruction="Solve the problem step-by-step, explaining your reasoning clearly in comments.")
        
        test_result = await self.code_runner(code_to_test=solution_code)
        
        if not test_result.is_correct:
            # If the initial solution fails, use CodeFix to generate a corrected version
            fixed_code = await self.code_fix(code=solution_code, error_message=test_result.error_message)
            # Re-run the fixed code to ensure correctness
            test_result = await self.code_runner(code_to_test=fixed_code)
            
            # Optional: if still failing, we could loop again — but per task, one fix is sufficient
            # Since the instruction says "use Generate-Test-Fix", we assume one fix suffices
            return fixed_code
        
        # If initial solution passed, return it
        return solution_code