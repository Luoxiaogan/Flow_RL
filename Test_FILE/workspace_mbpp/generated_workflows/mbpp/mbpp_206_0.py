# Workflow ID: mbpp_206_0
# Benchmark: mbpp
# Data Indices: [341, 284]

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
            "First, outline the algorithm step-by-step in natural language. "
            "Include how to handle edge cases such as empty lists, duplicates, or single elements. "
            "Then, based on this plan, generate actual Python code."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate the actual implementation
        code_instruction = (
            "Now implement the solution in Python based on the following plan:\n\n"
            f"{plan}\n\n"
            "Ensure the code is clear, efficient, and handles all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Run tests on the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Re-test after fixing
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, fall back to an ensemble approach with multiple strategies
                strategies = [
                    {"generation_pattern": "modular", "strategies": ["decompose_problem", "implement_helpers"]},
                    {"generation_pattern": "incremental", "strategies": ["analyze_requirements", "handle_edge_cases"]},
                    {"generation_pattern": "recursive", "strategies": ["break_down_recursive", "base_case_handling"]}
                ]
                solutions = []
                for strategy in strategies:
                    custom_op = operator.FlexibleCustom(
                        self.config, self.problem,
                        generation_pattern=strategy["generation_pattern"],
                        strategies=strategy["strategies"]
                    )
                    try:
                        gen_code = await custom_op(custom_instruction="Generate a robust solution using this pattern.")
                        solutions.append(gen_code)
                    except Exception:
                        pass  # Skip failed attempts gracefully

                # If we have valid solutions, choose the best one
                if solutions:
                    best_code = await self.sc_ensemble(solutions=solutions)
                    return best_code
                else:
                    return fixed_code  # fallback to the last known fix

        # Step 5: If the initial code passed, return it
        return initial_code