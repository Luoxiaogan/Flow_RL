# Workflow ID: mbpp_136_0
# Benchmark: mbpp
# Data Indices: [253, 44]

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
            "First, outline the algorithm step-by-step in plain English. "
            "Include how to handle edge cases (e.g., empty list, single element). "
            "Then, describe how to convert an arbitrary list into a heap using the heap queue algorithm."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            "Now, write a Python function that implements the plan above. "
            "Ensure it handles all edge cases mentioned in the plan. "
            "Use clear comments to reflect each part of the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, attempt to fix it
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
                # Fallback: Try generating again with a different approach
                alternate_plan = await self.code_generate(
                    instruction="Provide an alternative implementation strategy using a different method (e.g., iterative vs recursive, manual heapify vs heapq module)."
                )
                alternate_code = await self.code_generate(
                    instruction=f"Implement the following plan: {alternate_plan}"
                )
                # Ensemble: Compare both solutions and pick the best one
                solutions = [fixed_code, alternate_code]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code

        # Step 5: If successful, return the original code
        return initial_code