# Workflow ID: mbpp_162_0
# Benchmark: mbpp
# Data Indices: [260]

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
            "Outline a clear algorithm to find all anagrams of a string in a given list of strings. "
            "Include steps for sorting characters, comparing with target, handling edge cases like empty strings or duplicates, "
            "and explain how to use lambda functions effectively."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code using a flexible custom approach
        # We'll use the "modular" pattern to break down logic into helper functions
        code_generation_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Implement a solution using lambda functions to check anagrams. "
            "Ensure the main function accepts a string and a list of strings as inputs. "
            "Handle edge cases such as empty input lists or strings."
        )
        
        # Use FlexibleCustom with modular strategy to ensure structured, maintainable code
        code = await self.flexible_custom(
            custom_instruction=code_generation_instruction,
            generation_pattern="modular",
            strategies=["decompose_problem", "implement_helpers", "combine_solution"],
            use_structured_output=True
        )

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=code)

        # Step 4: If it fails, attempt to fix based on error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=code, error_message=test_result.error_message)
            # Optional: Re-test the fixed version
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if retest_result.is_correct:
                code = fixed_code

        return code