# Workflow ID: mbpp_70_0
# Benchmark: mbpp
# Data Indices: [191]

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
        # Initial solution generation
        code = await self.code_generate(instruction="Provide a straightforward solution to count the number of lists in a given list of lists.")

        # Iterative refinement loop (2-3 iterations as required)
        for iteration in range(2):  # Loop 2 times for refinement
            test_result = await self.code_runner(code_to_test=code)
            if test_result.is_correct:
                return code  # Success! Return the correct code
            
            # If not correct, fix based on error message
            code = await self.code_fix(code=code, error_message=test_result.error_message)

        # Final test after refinement loop
        final_test = await self.code_runner(code_to_test=code)
        if final_test.is_correct:
            return code
        
        # Fallback: if still failing, try one last time with flexible custom approach
        final_code = await self.flexible_custom(
            custom_instruction="Attempt to fix remaining issues using structured reasoning.",
            generation_pattern="incremental",
            strategies=["analyze_requirements", "handle_edge_cases"],
            max_refinements=1
        )
        
        return final_code