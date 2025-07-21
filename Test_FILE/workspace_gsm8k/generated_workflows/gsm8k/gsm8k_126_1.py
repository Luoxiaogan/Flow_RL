# Workflow ID: gsm8k_126_1
# Benchmark: gsm8k
# Data Indices: [580, 173, 520]

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
        This workflow uses the 'Reflect and Regenerate' pattern with a twist: 
        it first generates an initial solution, then reflects on it to uncover hidden assumptions or errors.
        Instead of just one re-solution, it uses a loop to generate multiple improved solutions based on that reflection,
        and finally selects the best one using ScEnsemble — ensuring robustness through diversity.
        
        Key difference from existing: Uses reflection not just once, but to fuel iterative refinement via parallel attempts.
        """
        # Step 1: Generate initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Reflect critically on the initial solution
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate multiple refined solutions using the same reflection as guidance
        refined_solutions = []
        for i in range(3):  # Create 3 different approaches informed by the same reflection
            refined = await self.custom(
                instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                            "Generate a new solution that addresses these points. Focus on clarity, logical flow, and correctness."
            )
            refined_solutions.append(refined)

        # Step 4: Use ScEnsemble to pick the most accurate among the refined ones
        final_answer = await self.sc_ensemble(solutions=refined_solutions)

        return final_answer