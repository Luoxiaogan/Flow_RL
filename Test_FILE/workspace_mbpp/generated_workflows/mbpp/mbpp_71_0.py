# Workflow ID: mbpp_71_0
# Benchmark: mbpp
# Data Indices: [199, 150]

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
        # Step 1: Generate a high-level plan in natural language (no code yet)
        planning_instruction = (
            "Outline the algorithm to solve this problem step-by-step. "
            "Include the core logic, edge cases, and any assumptions. "
            "Do not write code—just explain how you would approach it."
        )
        high_level_plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n\n{high_level_plan}\n\n"
            "Write a complete Python function that solves the problem. "
            "Include comments explaining key steps and handle all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Re-test the fixed code
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, use flexible custom with iterative refinement
                refined_code = await self.flexible_custom(
                    custom_instruction="Refine the solution based on the previous failure",
                    strategies=["analyze_requirements", "handle_edge_cases"],
                    max_refinements=2
                )
                return refined_code

        # Step 5: If it passes, return the original code
        return initial_code