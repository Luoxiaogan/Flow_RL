# Workflow ID: gsm8k_278_0
# Benchmark: gsm8k
# Data Indices: [970, 426, 273]

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
        Diverse and efficient workflow using Reflect + FlexibleCustom (Iterative Pattern).
        This approach first generates an initial solution, reflects on it to identify potential flaws,
        then uses iterative refinement via FlexibleCustom to improve the answer.
        """
        # Step 1: Generate initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Be explicit about each calculation."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use FlexibleCustom in iterative mode to refine the solution based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on this reflection: {reflection}, now solve the problem again with improved logic.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        return refined_solution