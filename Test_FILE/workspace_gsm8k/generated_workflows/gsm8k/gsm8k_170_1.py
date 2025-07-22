# Workflow ID: gsm8k_170_1
# Benchmark: gsm8k
# Data Indices: [395, 587]

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
        This is a diverse and efficient workflow using the Parallel Ensemble + Reflect & Regenerate pattern.
        It first generates multiple independent solutions to avoid single-point failures, then uses reflection to refine the best one.
        This logic differs from the existing workflow by introducing parallelism before refinement — not just one solution followed by reflection.
        """

        # Step 1: Generate 3 independent solutions in parallel (fan-out)
        solution_1 = await self.custom(instruction="Solve the problem step-by-step with clear reasoning.")
        solution_2 = await self.custom(instruction="Approach this problem using systematic decomposition: identify knowns, unknowns, and operations.")
        solution_3 = await self.custom(instruction="Begin by defining variables for all quantities mentioned. Then solve algebraically.")

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        candidate_solutions = [solution_1, solution_2, solution_3]
        best_solution = await self.sc_ensemble(solutions=candidate_solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or edge cases
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final custom generation — now informed by both ensemble selection and meta-cognition
        final_answer = await self.custom(
            instruction=f"Based on the following best solution and reflection: {reflection}. Now provide a fully revised answer that addresses any overlooked aspects."
        )

        return final_answer