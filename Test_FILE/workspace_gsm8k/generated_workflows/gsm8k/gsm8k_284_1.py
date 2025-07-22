# Workflow ID: gsm8k_284_1
# Benchmark: gsm8k
# Data Indices: [684, 391]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern combined with Parallel Ensemble.
        It first generates 3 independent solutions (parallel), then selects the best one via ScEnsemble.
        The selected solution is reflected upon to identify potential flaws or improvements.
        Based on that reflection, a new, improved solution is generated — this mimics human meta-cognition.
        This approach combines both ensemble robustness and reflective refinement for high-quality outputs.
        """

        # Step 1: Generate multiple diverse initial solutions in parallel (fan-out)
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: structured breakdown
                sol = await self.flexible_custom(
                    custom_instruction="Break down the problem step-by-step",
                    reasoning_pattern="sequential",
                    steps=["understand", "identify", "compute", "verify"]
                )
            elif i == 1:
                # Iterative refinement: start rough, improve over time
                sol = await self.flexible_custom(
                    custom_instruction="Start with an estimate, then refine",
                    reasoning_pattern="iterative",
                    steps=["rough_estimate", "improve", "validate"],
                    max_iterations=2
                )
            else:
                # Branching logic: explore alternative interpretations before deciding
                sol = await self.flexible_custom(
                    custom_instruction="Consider multiple possible approaches",
                    reasoning_pattern="branching",
                    steps=["analyze_options", "compare", "select"]
                )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the most consistent solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the chosen solution — don't rewrite yet!
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution based on the reflection — this is the core of the "Reflect-and-Regenerate" pattern
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution:\n\n{reflection}\n\nUse this insight to generate a refined, improved answer."
        )

        return final_answer