# Workflow ID: mbpp_109_0
# Benchmark: mbpp
# Data Indices: [87]

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
            "First, outline the algorithm to compute the length of a complex number. "
            "Include: definition of complex number length (magnitude), how to handle real/imaginary parts, "
            "and any edge cases like zero or negative values. Write in clear natural language."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual code
        code_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Write a Python function that computes the length (magnitude) of a complex number. "
            "Use the formula: sqrt(real^2 + imag^2). Handle edge cases explicitly in comments."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)
        
        if not test_result.is_correct:
            # Step 4: Fix based on error message
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            
            # Optional: Re-test after fix
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if not retest_result.is_correct:
                # If still failing, try an ensemble approach with multiple strategies
                solutions = [
                    await self.code_generate(instruction="Implement using math.sqrt for precision."),
                    await self.flexible_custom(
                        custom_instruction="Use modular approach: separate magnitude calculation from input validation.",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "implement_helpers"]
                    ),
                    fixed_code  # keep the fixed version as a baseline
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code
            
            return fixed_code
        
        return initial_code