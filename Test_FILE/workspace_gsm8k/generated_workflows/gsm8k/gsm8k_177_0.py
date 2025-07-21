# Workflow ID: gsm8k_177_0
# Benchmark: gsm8k
# Data Indices: [26, 338, 396]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It generates an initial solution, critically reflects on it, then uses that reflection
        to produce a superior final answer — mimicking human meta-cognition for improved accuracy.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying all relationships in the problem and solving step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "map_relationships", "solve_step_by_step", "verify"]
        )

        # Step 2: Reflect critically on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, more informed solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                       f"Reconstruct the answer with greater precision, ensuring no logical gaps or assumptions are missed."
        )

        return final_solution