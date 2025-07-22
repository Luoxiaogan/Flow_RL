# Workflow ID: mbpp_101_0
# Benchmark: mbpp
# Data Indices: [114, 238]

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
        This is a diverse workflow that first plans the solution in natural language,
        then generates code based on that plan. It includes fallbacks for failure.
        Uses a hybrid of Generate-Test-Fix and Parallel Ensemble patterns.
        """
        # Step 1: Generate a high-level plan (natural language outline)
        planning_instruction = (
            "Outline the algorithm step-by-step in plain English: "
            "What are the inputs? What transformations are needed? "
            "What edge cases must be handled? How will you validate correctness?"
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual Python code
        code_generation_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Write a Python function that solves the problem. "
            "Include clear comments explaining each part of the implementation."
        )
        initial_code = await self.code_generate(instruction=code_generation_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        if test_result.is_correct:
            return initial_code

        # Step 4: If it fails, attempt to fix using error message
        fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)

        # Step 5: Re-test the fixed version
        test_result_fixed = await self.code_runner(code_to_test=fixed_code)
        if test_result_fixed.is_correct:
            return fixed_code

        # Step 6: Fallback to ensemble — generate multiple strategies and pick best
        # Strategy 1: Incremental approach
        incremental_code = await self.flexible_custom(
            custom_instruction="Build the solution incrementally with unit tests",
            generation_pattern="incremental",
            strategies=["analyze_requirements", "handle_edge_cases"]
        )

        # Strategy 2: Modular decomposition
        modular_code = await self.flexible_custom(
            custom_instruction="Break the problem into reusable helper functions",
            generation_pattern="modular",
            strategies=["decompose_problem", "implement_helpers"]
        )

        # Strategy 3: Recursive logic (if applicable)
        recursive_code = await self.flexible_custom(
            custom_instruction="Solve using a recursive approach",
            generation_pattern="recursive",
            strategies=["understand_base_case", "define_recursive_step"]
        )

        # Combine all solutions into an ensemble
        solutions = [initial_code, fixed_code, incremental_code, modular_code, recursive_code]
        best_code = await self.sc_ensemble(solutions=solutions)

        # Final test before returning
        final_test = await self.code_runner(code_to_test=best_code)
        if final_test.is_correct:
            return best_code

        # Last resort: Return the best we have, even if not fully correct
        return best_code