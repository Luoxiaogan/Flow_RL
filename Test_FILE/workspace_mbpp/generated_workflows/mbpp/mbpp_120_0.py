# Workflow ID: mbpp_120_0
# Benchmark: mbpp
# Data Indices: [153, 161]

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
        This is a workflow graph for code generation using iterative refinement.
        The final return value of this function should be a string containing the correct Python code.
        """
        # Step 1: Generate an initial solution
        code = await self.code_generate(instruction="Provide a straightforward solution to find common index elements from three lists.")
        
        # Step 2: Iterative Test-Fix Loop (2-3 times max)
        for iteration in range(2):  # Loop 2 times for refinement
            test_result = await self.code_runner(code_to_test=code)
            
            if test_result.is_correct:
                # Success! Exit early
                return code
            
            # If not correct, fix the code using error message
            code = await self.code_fix(code=code, error_message=test_result.error_message)
        
        # Final attempt: Run one last test to ensure we return something valid
        final_test = await self.code_runner(code_to_test=code)
        if not final_test.is_correct:
            # Fallback: Use FlexibleCustom with "incremental" pattern for robustness
            code = await self.flexible_custom(
                custom_instruction="Rebuild solution incrementally based on feedback",
                generation_pattern="incremental",
                strategies=["analyze_requirements", "handle_edge_cases"],
                max_refinements=1
            )
        
        return code