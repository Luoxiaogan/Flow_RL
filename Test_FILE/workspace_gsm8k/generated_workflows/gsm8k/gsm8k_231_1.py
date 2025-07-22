# Workflow ID: gsm8k_231_1
# Benchmark: gsm8k
# Data Indices: [694, 24]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and effective workflow using a hybrid of:
        1. Parallel Ensemble (Fan-out/Fan-in) to generate multiple independent solutions
        2. Reflect and Regenerate pattern to improve the best solution based on critical feedback
        3. Conditional logic: if reflection indicates high confidence, skip regeneration; otherwise, regenerate
        
        The structure ensures robustness through diversity (multiple approaches), meta-cognition (reflection), 
        and intelligent iteration — all while avoiding the single-solution-first approach of the existing workflow.
        """

        # Step 1: Generate 3 parallel solutions using different reasoning patterns via FlexibleCustom
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            step_list = {
                "sequential": ["identify_knowns", "formulate_plan", "execute_calculation", "verify"],
                "iterative": ["initial_guess", "refine_step", "final_check"],
                "branching": ["analyze_case_a", "analyze_case_b", "combine_results"]
            }[pattern]

            sol = await self.flexible_custom(
                custom_instruction="Solve this math word problem with clear reasoning steps.",
                reasoning_pattern=pattern,
                steps=step_list
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the best solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Conditional logic: If reflection suggests low confidence or ambiguity, regenerate
        # Otherwise, return the best solution directly — avoids unnecessary work when confident
        if "uncertain" in reflection.lower() or "ambiguous" in reflection.lower() or "error" in reflection.lower():
            final_solution = await self.custom(
                instruction=f"Based on the following reflection: '{reflection}'. "
                            f"Re-solve the problem from scratch, ensuring rigorous logical flow and clarity."
            )
        else:
            final_solution = best_solution

        return final_solution