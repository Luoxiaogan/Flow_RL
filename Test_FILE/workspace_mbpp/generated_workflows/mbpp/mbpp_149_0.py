# Workflow ID: mbpp_149_0
# Benchmark: mbpp
# Data Indices: [141, 208]

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
            "First, outline the algorithm and edge cases for solving this problem. "
            "Explain how you would approach it step-by-step, including any mathematical formulas or logic needed. "
            "Do not write code yet—focus on the reasoning process."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Now write a complete, correct Python function that solves the problem. "
            "Include clear comments explaining each part of the implementation. "
            "Handle all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Re-test the fixed version
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, try an ensemble approach with multiple strategies
                solutions = [
                    await self.code_generate(instruction="Solve using a different approach based on the plan."),
                    await self.code_generate(instruction="Implement a more robust version with additional error handling."),
                    await self.flexible_custom(
                        custom_instruction="Apply modular decomposition to improve clarity and correctness.",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                    )
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                final_test = await self.code_runner(code_to_test=best_code)
                if final_test.is_correct:
                    return best_code
                else:
                    # Last resort: use flexible custom with test-driven strategy
                    final_code = await self.flexible_custom(
                        custom_instruction="Use a test-driven approach to ensure correctness.",
                        generation_pattern="test_driven",
                        strategies=["understand_tests", "implement_minimum", "refactor"],
                        max_refinements=2
                    )
                    return final_code

        # Step 5: If the initial code passes, return it
        return initial_code