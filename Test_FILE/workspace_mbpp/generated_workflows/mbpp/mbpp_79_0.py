# Workflow ID: mbpp_79_0
# Benchmark: mbpp
# Data Indices: [273, 299]

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
        This is a diverse workflow graph for code generation that first outlines the solution plan,
        then generates code based on that plan, and finally refines it using iterative testing.
        """
        # Step 1: Generate a high-level plan in natural language
        planning_instruction = (
            "Outline a clear algorithm to solve this problem. Include steps, edge cases, "
            "and how to validate correctness. Do not write any code yet."
        )
        plan = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual Python code
        code_instruction = (
            f"Based on this plan:\n{plan}\n"
            "Now write a complete Python function that solves the problem. "
            "Include comments explaining each major section of the code."
        )
        initial_code = await self.code_generate(instruction=code_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If the code fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(code=initial_code, error_message=test_result.error_message)
            # Optional: Re-test after fixing
            retest_result = await self.code_runner(code_to_test=fixed_code)
            if not retest_result.is_correct:
                # Fallback: Try an ensemble approach with multiple strategies
                solutions = [
                    await self.flexible_custom(
                        custom_instruction="Use a modular approach to break down the problem",
                        generation_pattern="modular",
                        strategies=["decompose_problem", "implement_helpers", "combine_solution"]
                    ),
                    await self.flexible_custom(
                        custom_instruction="Apply an incremental strategy focusing on core logic first",
                        generation_pattern="incremental",
                        strategies=["analyze_requirements", "build_step_by_step", "validate_each_step"]
                    )
                ]
                best_code = await self.sc_ensemble(solutions=solutions)
                return best_code
            else:
                return fixed_code
        else:
            return initial_code