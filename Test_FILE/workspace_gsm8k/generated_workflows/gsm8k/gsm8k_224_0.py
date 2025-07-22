# Workflow ID: gsm8k_224_0
# Benchmark: gsm8k
# Data Indices: [169, 651]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions using FlexibleCustom in parallel mode.
        Step 2: Select the best one via ScEnsemble.
        Step 3: Reflect on its potential flaws or assumptions.
        Step 4: Use reflection to guide a final refined solution via Custom.
        """

        # --- PART 1: Parallel Ensemble (Fan-out) ---
        solution_candidates = []
        for i in range(3):
            candidate = await self.flexible_custom(
                custom_instruction="Apply systematic reasoning to solve the problem.",
                reasoning_pattern="parallel",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_candidates.append(candidate)

        # --- PART 2: Select Best Candidate ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- PART 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- PART 4: Regenerate Based on Reflection (Reflect-and-Regenerate Pattern) ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution:\n{best_solution}\n\nAnd the following reflection on possible weaknesses or oversights:\n{reflection}\n\nNow, provide a fully revised and improved answer based on this critique."
        )

        return final_answer