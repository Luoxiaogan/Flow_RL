# Workflow ID: mbpp_91_0
# Benchmark: mbpp
# Data Indices: [54, 159]

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
        # Step 1: Generate a high-level plan in natural language
        planning_instruction = (
            "Outline the algorithm step-by-step in plain English. "
            "Include the approach (e.g., mathematical formula or iterative loop), "
            "how to handle edge cases (like n=0 or empty arrays), and any assumptions."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Write a clean, efficient, and well-commented Python function that solves the problem. "
            "Handle all edge cases explicitly. Do not include test cases or example inputs."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # Step 4: If it fails, attempt to fix using the error message
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            
            # Optional: Re-test the fixed code
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if not retest_result.is_correct:
                # Fallback: Use flexible custom with modular strategy to rebuild
                modular_code = await self.flexible_custom(
                    custom_instruction="Rebuild solution by decomposing into reusable functions",
                    generation_pattern="modular",
                    strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                )
                return modular_code
            
            return fixed_code
        
        return initial_code