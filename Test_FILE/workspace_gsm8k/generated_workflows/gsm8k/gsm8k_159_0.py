# Workflow ID: gsm8k_159_0
# Benchmark: gsm8k
# Data Indices: [143, 760]

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
        Diverse and efficient workflow using iterative refinement with a structured approach.
        This uses FlexibleCustom in 'iterative' mode to systematically improve the solution.
        The structure ensures logical progression without unnecessary complexity — just 4 steps total.
        """
        # Step 1: Use iterative FlexibleCustom for systematic reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Apply a step-by-step reasoning process.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a final, improved Custom call
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be clear, concise, and accurate."
        )

        return final_answer