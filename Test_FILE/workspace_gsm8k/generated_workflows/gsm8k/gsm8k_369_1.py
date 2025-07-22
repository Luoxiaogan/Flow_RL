# Workflow ID: gsm8k_369_1
# Benchmark: gsm8k
# Data Indices: [957, 736, 340]

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
        This is a diverse and efficient workflow using the Iterative Refinement pattern.
        It starts with a simple initial solution and applies progressive improvements through two Review steps.
        This logic differs from the existing workflow by focusing on iterative refinement instead of reflection-based regeneration.
        """
        # Step 1: Generate an initial solution with minimal guidance—just ask to solve it
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be concise but clear."
        )

        # Step 2: Apply first review to improve clarity and correctness
        first_revision = await self.review(pre_solution=initial_solution)

        # Step 3: Apply second review to catch subtle errors or missed assumptions
        second_revision = await self.review(pre_solution=first_revision)

        # Step 4: Return the final refined solution after two rounds of improvement
        return second_revision