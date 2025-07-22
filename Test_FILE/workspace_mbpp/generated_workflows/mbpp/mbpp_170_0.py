# Workflow ID: mbpp_170_0
# Benchmark: mbpp
# Data Indices: [110, 51]

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
            "Include how to handle edge cases such as negative numbers, zero, single-digit numbers, and empty inputs. "
            "Explain how to extract digits at even and odd positions (considering 0-based or 1-based indexing)."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n\n"
            "Write a clean, efficient Python function that implements the solution. "
            "Include clear comments explaining each major step. Handle all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test the fixed version
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, try a parallel ensemble approach with multiple strategies
                solutions = [
                    await self.code_generate(instruction="Implement using string conversion and index-based logic."),
                    await self.code_generate(instruction="Use mathematical division and modulo to extract digits."),
                    await self.flexible_custom(
                        custom_instruction="Apply modular decomposition strategy",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "handle_edge_cases"]
                    )
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # Step 5: If it passes, return the original code
        return initial_code