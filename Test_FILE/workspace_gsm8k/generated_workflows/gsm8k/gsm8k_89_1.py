# Workflow ID: gsm8k_89_1
# Benchmark: gsm8k
# Data Indices: [287, 939, 585]

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
        Diverse workflow combining Parallel Ensemble + Reflect + Iterative Refinement.
        1. Generate 3 independent solutions via parallel approach (fan-out).
        2. Use ScEnsemble to select the best one.
        3. Reflect on that best solution to uncover hidden flaws or assumptions.
        4. Use FlexibleCustom in iterative mode to refine it progressively.
        This creates a robust, meta-cognitive loop that improves both diversity and depth.
        """
        # Step 1: Generate multiple candidate solutions in parallel (fan-out)
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem by applying a different reasoning strategy each time: "
                            "first try step-by-step decomposition, then try visual modeling, then try algebraic setup."
            )
            solution_candidates.append(candidate)

        # Step 2: Select the best among them using ensemble evaluation
        best_candidate = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the selected solution to identify weaknesses
        reflection = await self.reflect(pre_solution=best_candidate)

        # Step 4: Use iterative refinement with FlexibleCustom to improve based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Refine the solution below based on this reflection: '{reflection}'. "
                               "Use an iterative approach: first analyze, then adjust, then verify.",
            reasoning_pattern="iterative",
            steps=["analyze", "adjust", "verify"],
            max_iterations=2
        )

        return refined_solution