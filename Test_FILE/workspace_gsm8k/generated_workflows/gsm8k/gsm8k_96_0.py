# Workflow ID: gsm8k_96_0
# Benchmark: gsm8k
# Data Indices: [623, 942]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate multiple solutions in parallel (fan-out).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect critically on the selected solution to uncover hidden flaws or assumptions.
        Step 4: Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Parallel Ensemble (Fan-out) ---
        solution_candidates = []
        for _ in range(3):  # Generate 3 different initial approaches
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into clear steps. Focus on identifying all given quantities and relationships."
            )
            solution_candidates.append(candidate)

        # --- STEP 2: Select Best Candidate ---
        best_initial = await self.sc_ensemble(solutions=solution_candidates)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_initial)

        # --- STEP 4: Regenerate Based on Reflection (Reflect-and-Regenerate Pattern) ---
        # Use FlexibleCustom with iterative reasoning pattern to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Given the following reflection: '{reflection}'. Now solve the problem again, focusing on addressing these points.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        return refined_solution