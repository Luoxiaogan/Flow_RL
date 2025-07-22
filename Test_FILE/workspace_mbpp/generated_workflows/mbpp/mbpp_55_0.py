# Workflow ID: mbpp_55_0
# Benchmark: mbpp
# Data Indices: [279, 241]

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
        This is a diverse workflow graph for code generation.
        It first outlines the plan in natural language, then generates code based on that plan.
        If the code fails, it attempts to fix it. If still failing, uses ensemble of multiple strategies.
        """
        # Step 1: Generate a high-level plan (natural language outline)
        plan_instruction = (
            "Outline the algorithm step-by-step in plain English. "
            "Include how to handle edge cases, what data structures to use, and the logic flow. "
            "Do not write any code yet."
        )
        plan = await self.code_generate(instruction=plan_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Write a complete, correct Python function to solve the problem. "
            "Include clear comments explaining each major section."
        )
        code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=code)

        # Step 4: If it fails, attempt to fix using error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=code, error_message=test_result.error_message)
            # Re-test the fixed version
            test_result = await self.code_runner(code_to_test=fixed_code)
            if not test_result.is_correct:
                # If still failing, try an ensemble approach with alternative strategies
                alternatives = [
                    await self.flexible_custom(
                        custom_instruction="Use a modular approach: break into helper functions",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                    ),
                    await self.flexible_custom(
                        custom_instruction="Use a recursive approach if applicable",
                        generation_pattern="recursive",
                        strategies=["handle_base_case", "define_recursion", "combine_results"]
                    ),
                    await self.code_generate(instruction="Solve using a brute-force method for verification")
                ]
                best_code = await self.sc_ensemble(solutions=alternatives)
                return best_code

        return fixed_code if not test_result.is_correct else code