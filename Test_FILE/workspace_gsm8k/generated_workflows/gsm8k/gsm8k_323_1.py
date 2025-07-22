# Workflow ID: gsm8k_323_1
# Benchmark: gsm8k
# Data Indices: [325, 12, 365]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate Loop
        - First, generate 3 independent solutions using different reasoning patterns (parallel).
        - Select the best one via ScEnsemble.
        - Critically reflect on it to uncover hidden assumptions or flaws.
        - Use that reflection to guide a targeted regen (not a full new solve) for final improvement.
        
        This combines:
        1. Parallel Ensemble (fan-out/fan-in): multiple initial strategies → best result
        2. Reflect-and-Regenerate: meta-cognition to refine the winner
        3. Conditional logic: uses reflection content to shape the next step
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different patterns
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem by focusing on clear logical steps.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if pattern == "iterative" else 1
            )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the chosen solution — don’t rewrite yet!
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on reflection, generate a refined version only where needed
        # This is not a full regen — it’s guided by the critique
        improved_solution = await self.custom(
            instruction=f"Given the following reflection about the current solution: '{reflection}'. "
                        f"Improve only the parts that are flawed or unclear. Keep everything else intact."
        )

        return improved_solution