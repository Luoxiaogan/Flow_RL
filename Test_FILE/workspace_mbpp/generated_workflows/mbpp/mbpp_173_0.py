# Workflow ID: mbpp_173_0
# Benchmark: mbpp
# Data Indices: [48, 10]

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
        # Step 1: Generate a high-level plan (natural language outline)
        planning_instruction = (
            "Outline the algorithm step-by-step in natural language. "
            "Include how to handle edge cases such as empty lists, invalid indices, or out-of-range bounds. "
            "Also describe how to validate inputs and ensure robustness."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a complete, correct Python function that implements the solution. "
            "Include clear comments explaining each major section of the code."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Run tests to check correctness
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Re-test the fixed version
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # If still failing, try generating an alternative approach via flexible custom
                alternative_code = await self.flexible_custom(
                    custom_instruction="Try solving with a modular decomposition strategy.",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                # Ensemble: compare original fixed code vs. modular alternative
                solutions = [fixed_code, alternative_code]
                final_code = await self.sc_ensemble(solutions=solutions)
                return final_code

        # Step 5: Return the best working code
        return initial_code if test_result.is_correct else fixed_code