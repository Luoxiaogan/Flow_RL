# Workflow ID: gsm8k_115_1
# Benchmark: gsm8k
# Data Indices: [266, 632]

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
        This is a diverse and robust workflow using the Reflect and Regenerate pattern.
        It first generates an initial solution, then critically reflects on it to identify potential flaws or improvements,
        and finally uses that reflection to guide a new, higher-quality solution. This meta-cognitive loop ensures deep reasoning
        and iterative improvement — a fundamentally different logic from ensemble-based approaches.
        """
        # Step 1: Generate an initial solution using general-purpose reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Do not rush — take time to ensure each step is logically sound."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to generate a refined solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution:\n\n{reflection}\n\nUse this insight to produce a more accurate, well-structured, and logically rigorous final answer."
        )

        return final_answer