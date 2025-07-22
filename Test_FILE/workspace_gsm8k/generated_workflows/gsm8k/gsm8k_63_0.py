# Workflow ID: gsm8k_63_0
# Benchmark: gsm8k
# Data Indices: [385, 81]

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
        Diverse and efficient workflow using iterative refinement with FlexibleCustom.
        This pattern ensures logical progression from initial reasoning to final solution.
        """
        # Step 1: Use FlexibleCustom in iterative mode to generate a structured, step-by-step solution
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear steps: analyze, plan, solve, verify.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or missing elements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a final, improved solution via Custom
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                       "Now, provide a refined and complete answer that addresses all aspects of the problem."
        )

        return final_solution