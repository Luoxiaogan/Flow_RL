# Workflow ID: mbpp_90_0
# Benchmark: mbpp
# Data Indices: [315, 192]

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
        # Step 1: Generate a high-level plan (natural language outline)
        planning_instruction = (
            "First, analyze the problem and write a detailed plan in natural language. "
            "Include the algorithm you will use, key steps, edge cases to consider, "
            "and any assumptions. Do not write code yet."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a complete, working Python function that solves the problem. "
            "Include comments explaining each part of the implementation. "
            "Handle all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test after fix
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # If still failing, try an ensemble approach with a fresh idea
                alternative_plan = await self.code_generate(
                    instruction="Provide an alternative algorithm or strategy to solve the same problem."
                )
                alt_code = await self.code_generate(
                    instruction=f"Implement the following alternative approach:\n{alternative_plan}"
                )
                solutions = [fixed_code, alt_code]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # Step 5: If successful, return the initial code
        return initial_code