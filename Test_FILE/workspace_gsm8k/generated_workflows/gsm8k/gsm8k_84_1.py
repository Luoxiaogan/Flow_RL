# Workflow ID: gsm8k_84_1
# Benchmark: gsm8k
# Data Indices: [61, 40]

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
        Efficient and diverse workflow using a branching logic with FlexibleCustom in 'branching' mode.
        This approach evaluates two distinct reasoning paths (algebraic vs. verbal) and selects the best one.
        - Step 1: Generate two solutions using FlexibleCustom with different reasoning patterns (sequential vs. branching).
        - Step 2: Use ScEnsemble to choose the better solution based on internal consistency and clarity.
        - Step 3: If the ensemble result is uncertain or weak, apply a single Review for refinement.
        
        This differs from the existing workflow by using branching reasoning as a primary strategy instead of iterative refinement or parallel ensemble alone.
        It avoids unnecessary complexity while ensuring logical diversity in how solutions are generated.
        """
        # --- Step 1: Generate two contrasting solutions ---
        solution_a = await self.flexible_custom(
            custom_instruction="Solve this problem by first identifying all knowns and unknowns, then setting up equations.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_variables", "formulate_equations", "solve"]
        )

        solution_b = await self.flexible_custom(
            custom_instruction="Solve this problem by thinking through it step-by-step in plain language without formal equations.",
            reasoning_pattern="branching",
            steps=["understand_context", "break_into_steps", "check_consistency", "finalize_answer"]
        )

        # --- Step 2: Ensemble to pick the best ---
        solutions = [solution_a, solution_b]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Optional final refinement if needed ---
        reflection = await self.reflect(pre_solution=best_solution)
        if "unclear" in reflection.lower() or "ambiguous" in reflection.lower():
            final_answer = await self.review(pre_solution=best_solution)
        else:
            final_answer = best_solution

        return final_answer