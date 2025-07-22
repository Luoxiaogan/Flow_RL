# Workflow ID: gsm8k_204_1
# Benchmark: gsm8k
# Data Indices: [665, 309]

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
        Diverse and efficient workflow using Reflect-and-Regenerate logic with a single custom call.
        This approach first generates an initial solution, then uses reflection to identify potential flaws or improvements,
        and finally creates a refined solution based on that insight — mimicking human meta-cognition in a lightweight, effective way.
        It avoids unnecessary loops or ensembles, focusing instead on intelligent iteration within a single cycle.
        """
        # Step 1: Generate an initial solution using a structured reasoning pattern
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "decompose", "solve", "validate"],
            custom_instruction="Solve the problem step-by-step while explaining your logic clearly."
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Provide a revised, more accurate answer based on this critique."
        )

        return final_solution