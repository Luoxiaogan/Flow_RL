# Workflow ID: gsm8k_50_1
# Benchmark: gsm8k
# Data Indices: [659, 912]

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
        Diverse and efficient workflow using a Parallel Ensemble followed by Reflect-and-Regenerate.
        This pattern leverages multiple independent reasoning paths (parallel) to increase robustness,
        then uses meta-cognition (reflection) to guide targeted improvement—avoiding blind iteration
        and instead focusing on the most promising solution path. Combines two distinct design patterns:
        1. Parallel Ensemble: Generate 3 diverse initial solutions.
        2. Reflect-and-Regenerate: Critique the best one and rebuild it with insight.
        """
        # Step 1: Generate 3 parallel solutions using FlexibleCustom in different reasoning modes
        # Each uses a unique strategy to avoid redundancy and promote diversity
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem step-by-step with clear reasoning.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if pattern == "iterative" else 1
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the best solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution to uncover hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution based on both the original and the reflection
        final_answer = await self.custom(
            instruction=f"Given the following initial solution:\n{best_solution}\n\n"
                        f"And the following reflection on its potential weaknesses:\n{reflection}\n\n"
                        "Now, produce a refined, improved answer that addresses these concerns."
        )

        return final_answer