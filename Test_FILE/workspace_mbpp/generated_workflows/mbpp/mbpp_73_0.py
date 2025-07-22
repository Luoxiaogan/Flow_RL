# Workflow ID: mbpp_73_0
# Benchmark: mbpp
# Data Indices: [330, 291]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.code_generate = operator.CustomCodeGenerate(self.config, self.problem)
        self.code_runner = operator.CodeRunner(self.config, self.problem)
        self.code_fix = operator.CodeFix(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and thoughtful workflow for code generation.
        It first creates a plan in natural language, then generates code based on that plan.
        If the code fails, it uses a fix loop. If needed, it falls back to an ensemble of solutions.
        """
        # Step 1: Generate a high-level plan (algorithm + edge cases) in natural language
        planning_instruction = (
            "Outline the algorithm, key steps, and potential edge cases for solving this problem. "
            "Do not write code yet — focus on reasoning and structure."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual Python code
        code_generation_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Now write the Python function to solve the problem. Include comments explaining each step."
        )
        initial_code = await self.code_generate(instruction=code_generation_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it once
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Re-test the fixed code
            test_result = await self.code_runner(code_to_test=fixed_code)
            if test_result.is_correct:
                return fixed_code

        # Step 5: If still failing, try an ensemble approach with multiple strategies
        if not test_result.is_correct:
            # Generate 2 alternative approaches using flexible_custom with different patterns
            strategy1 = await self.flexible_custom(
                custom_instruction="Use modular decomposition to solve the problem.",
                generation_pattern="modular",
                strategies=["decompose_problem", "implement_helpers", "combine_solution"]
            )

            strategy2 = await self.flexible_custom(
                custom_instruction="Solve incrementally, focusing on correctness over optimization.",
                generation_pattern="incremental",
                strategies=["analyze_requirements", "handle_edge_cases"]
            )

            # Add original failed code as fallback
            solutions = [strategy1, strategy2, initial_code]
            best_code = await self.sc_ensemble(solutions=solutions)
            
            # Final test
            final_test = await self.code_runner(code_to_test=best_code)
            if final_test.is_correct:
                return best_code

        # If all else passes, return the initial code (it passed!)
        return initial_code