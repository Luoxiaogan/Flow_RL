# Workflow ID: gsm8k_137_1
# Benchmark: gsm8k
# Data Indices: [831, 852]

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
        This is a diverse workflow using the Iterative Refinement pattern with repeated Review steps.
        It starts with a simple initial solution and applies progressive improvements via Review,
        ensuring logical depth through multiple rounds of refinement without reflection-based branching.
        The structure is simple yet effective: generate → review → review → return.
        """
        # Step 1: Generate an initial solution using a basic custom call (no complex reasoning pattern)
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations clearly."
        )

        # Step 2: First round of iterative refinement — improve based on internal critique
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second round of refinement — further polish for clarity, correctness, and completeness
        second_refined = await self.review(pre_solution=first_refined)

        # Step 4: Return the final improved solution after two rounds of review
        return second_refined