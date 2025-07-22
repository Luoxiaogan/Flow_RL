# Workflow ID: mbpp_145_0
# Benchmark: mbpp
# Data Indices: [198, 30]

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
            "Outline the algorithm to solve this problem step-by-step. "
            "Include key steps, edge cases, and any assumptions you're making. "
            "Do not write code yet."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n\n{plan}\n\n"
            "Write a complete, working Python function that solves the problem. "
            "Include comments explaining each major section of the code."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using error message
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
                # Fallback: Try an ensemble approach with multiple strategies
                strategies = [
                    "incremental",
                    "modular",
                    "recursive",
                    "test_driven"
                ]
                solutions = []
                for strategy in strategies:
                    custom_instruction = (
                        f"Use {strategy} pattern to solve the problem. "
                        "Focus on clarity, correctness, and handling edge cases."
                    )
                    try:
                        solution = await self.flexible_custom(
                            custom_instruction=custom_instruction,
                            generation_pattern=strategy,
                            strategies=["analyze_requirements", "handle_edge_cases"],
                            max_refinements=1
                        )
                        solutions.append(solution)
                    except Exception:
                        pass  # Skip failed attempts gracefully

                if solutions:
                    best_code = await self.sc_ensemble(solutions=solutions)
                    # Final test before returning
                    final_test = await self.code_runner(code_to_test=best_code)
                    if final_test.is_correct:
                        return best_code

                # If all else fails, return the fixed version (even if it might still fail)
                return fixed_code

        # Step 5: Return the original or corrected code if successful
        return initial_code