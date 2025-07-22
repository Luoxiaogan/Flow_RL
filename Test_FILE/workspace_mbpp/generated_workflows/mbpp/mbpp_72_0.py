# Workflow ID: mbpp_72_0
# Benchmark: mbpp
# Data Indices: [99]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.code_generate = operator.CustomCodeGenerate(self.config, self.problem)
        self.code_runner = operator.CodeRunner(self.config, self.problem)
        self.code_fix = operator.CodeFix(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse workflow for code generation that emphasizes thoughtful planning before coding.
        It uses a two-step generation approach: first outline the plan in natural language, then generate code based on that plan.
        If the generated code fails, it fixes it using the error message. This ensures high-quality, well-reasoned solutions.
        """
        # Step 1: Generate a detailed plan (natural language description of algorithm and edge cases)
        planning_instruction = (
            "Outline the algorithm step-by-step in plain English. "
            "Include how to handle edge cases such as empty lists, ranges with equal bounds, or invalid inputs. "
            "Explain what each part of the solution will do."
        )
        planning_code = await self.code_generate(instruction=planning_instruction)

        # Step 2: Use the plan to generate actual Python code
        code_generation_instruction = (
            f"Based on this plan:\n{planning_code}\n"
            "Write a Python function that counts elements in a list within a given range (inclusive). "
            "Ensure it handles all edge cases mentioned in the plan. Add clear comments explaining each section."
        )
        initial_code = await self.code_generate(instruction=code_generation_instruction)

        # Step 3: Test the generated code
        test_result = await self.code_runner(code_to_test=initial_code)

        # Step 4: If it fails, fix it using the error message
        if not test_result.is_correct:
            fixed_code = await self.code_fix(
                code=initial_code,
                error_message=test_result.error_message
            )
            # Optional: Run one more test after fixing
            final_test = await self.code_runner(code_to_test=fixed_code)
            if final_test.is_correct:
                return fixed_code
            else:
                # Fallback: use ensemble to pick from multiple attempts
                alternative_solutions = [
                    initial_code,
                    fixed_code,
                    await self.code_generate(instruction="Re-write the solution focusing on robustness and clarity.")
                ]
                best_code = await self.sc_ensemble(solutions=alternative_solutions)
                return best_code

        # If initial code passed, return it
        return initial_code