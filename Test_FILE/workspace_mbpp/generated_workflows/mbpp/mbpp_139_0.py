# Workflow ID: mbpp_139_0
# Benchmark: mbpp
# Data Indices: [124]

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
        # Use FlexibleCustom with a modular strategy to build a clean, reusable solution
        # This pattern ensures decomposition and clarity without overcomplicating the initial attempt
        modular_code = await self.flexible_custom(
            custom_instruction="Break down the problem into helper functions: one for regex matching, one for extracting values.",
            generation_pattern="modular",
            strategies=["decompose_problem", "implement_helpers", "combine_solution"]
        )

        # Run the test to validate correctness
        test_result = await self.code_runner(code_to_test=modular_code)

        # If it fails, use CodeFix to address the specific error
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=modular_code,
                error_message=test_result.error_message
            )
            return fixed_code

        # If it passes, return the modular solution as-is
        return modular_code