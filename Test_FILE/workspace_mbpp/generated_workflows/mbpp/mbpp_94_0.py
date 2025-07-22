# Workflow ID: mbpp_94_0
# Benchmark: mbpp
# Data Indices: [295]

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
            "Outline a clear plan to solve the problem. "
            "Describe the algorithm step-by-step, including how you'll handle edge cases like empty lists or single-element tuples."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a Python function that sorts a list of non-empty tuples by their last element in increasing order."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix using error message
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
                # If still failing, fall back to an ensemble approach with multiple strategies
                solutions = [
                    await self.code_generate(instruction="Use sorted() with key=lambda x: x[-1]"),
                    await self.code_generate(instruction="Implement custom sorting logic manually"),
                    await self.flexible_custom(
                        custom_instruction="Apply a modular approach: separate extraction and sorting",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                    )
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                final_result = await self.code_runner(code_to_test=best_code)
                if final_result.is_correct:
                    return best_code
                else:
                    # Last resort: try one more fix
                    return await self.code_fix(code=best_code, error_message=final_result.error_message)

        # Step 5: Return the original code if it passed all tests
        return initial_code