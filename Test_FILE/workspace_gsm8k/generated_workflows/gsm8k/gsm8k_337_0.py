# Workflow ID: gsm8k_337_0
# Benchmark: gsm8k
# Data Indices: [469, 17]

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
        This is a diverse and iterative refinement-based workflow.
        It starts with an initial solution, then applies Review twice to progressively improve it.
        The structure mimics how humans refine their thinking: first draft → critique → revision → second critique → final polish.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying what needs to be calculated and break the problem into logical steps.",
            reasoning_pattern="sequential",
            steps=["understand_problem", "identify_knowns", "formulate_plan", "execute_calculation"]
        )

        # Step 2: First review to catch obvious errors or missing logic
        first_revision = await self.review(pre_solution=initial_solution)

        # Step 3: Second review for deeper clarity, structure, and precision
        second_revision = await self.review(pre_solution=first_revision)

        # Step 4: Return the fully refined solution (no need for ensemble here — iterative refinement is sufficient)
        return second_revision