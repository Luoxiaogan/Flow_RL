# Workflow ID: mbpp_164_0
# Benchmark: mbpp
# Data Indices: [317, 216]

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
            "First, outline the algorithm and edge cases in plain English. "
            "Describe how you would solve this problem step-by-step, including any assumptions or special conditions."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on the following plan:\n{plan}\n"
            "Write a complete, correct Python function that solves the problem. "
            "Include clear comments explaining key logic and handle all edge cases mentioned in the plan."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test the fixed code to ensure correctness
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                return fixed_code
            else:
                # Fallback: Use flexible custom with test-driven strategy as last resort
                self.flexible_custom = operator.FlexibleCustom(
                    self.config, 
                    self.problem,
                    generation_pattern="test_driven",
                    strategies=["understand_tests", "implement_minimum", "refactor"]
                )
                final_code = await self.flexible_custom(custom_instruction="Use a test-driven approach to build the solution incrementally.")
                return final_code

        # Step 5: If initial code passed, return it
        return initial_code