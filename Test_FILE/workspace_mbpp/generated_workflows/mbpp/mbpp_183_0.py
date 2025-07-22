# Workflow ID: mbpp_183_0
# Benchmark: mbpp
# Data Indices: [373, 121]

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
        It uses a two-phase plan-first approach with fallbacks and refinement.
        First, it generates a high-level plan in natural language.
        Then, it uses that plan to generate the actual code.
        If the code fails, it attempts to fix it.
        If still failing, it falls back to an ensemble of alternative strategies.
        """

        # Phase 1: Generate a detailed plan (natural language)
        plan_instruction = (
            "First, outline the algorithm step-by-step in plain English. "
            "Include how you would handle edge cases like empty inputs or single-element structures. "
            "Explain why this approach works and what its time/space complexity would be."
        )
        planning_output = await self.code_generate(instruction=plan_instruction)

        # Phase 2: Generate code based on the plan
        code_instruction = (
            f"Based on the following plan:\n{planning_output}\n"
            "Now write the actual Python code. Include clear comments explaining each part of the implementation."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Phase 3: Test the code
        test_result = await self.code_runner(code_to_test=initial_code)

        if test_result.is_correct:
            return initial_code

        # Phase 4: Attempt to fix the code using the error message
        fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)

        # Phase 5: Re-test the fixed code
        test_result_fixed = await self.code_runner(code_to_test=fixed_code)
        if test_result_fixed.is_correct:
            return fixed_code

        # Phase 6: Fallback to parallel ensemble — generate multiple approaches
        # Use FlexibleCustom with different patterns to explore diverse strategies
        strategies = [
            ("modular", ["decompose_problem", "implement_helpers", "combine_solution"]),
            ("test_driven", ["understand_tests", "implement_minimum", "refactor"]),
            ("incremental", ["build_step_by_step", "validate_each_step", "finalize"])
        ]

        solutions = []
        for pattern, strategy_list in strategies:
            custom_config = {
                "generation_pattern": pattern,
                "strategies": strategy_list,
                "use_structured_output": True
            }
            try:
                generated_code = await self.flexible_custom(
                    custom_instruction=f"Use {pattern} approach with strategies: {strategy_list}",
                    previous_results=solutions
                )
                solutions.append(generated_code)
            except Exception as e:
                # Skip failed attempts gracefully
                continue

        # If we have at least one valid solution, use ensemble to pick the best
        if solutions:
            best_code = await self.sc_ensemble(solutions=solutions)
            # Optional: Run final test on the best candidate
            final_test = await self.code_runner(code_to_test=best_code)
            if final_test.is_correct:
                return best_code

        # As a last resort, return the most recently fixed version
        return fixed_code