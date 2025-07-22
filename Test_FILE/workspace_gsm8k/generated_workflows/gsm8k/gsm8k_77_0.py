# Workflow ID: gsm8k_77_0
# Benchmark: gsm8k
# Data Indices: [48, 213, 106]

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
        This is a diverse workflow using Iterative Refinement with FlexibleCustom for structured reasoning.
        It starts with an initial solution, then applies Review twice to progressively improve it.
        The structure ensures logical progression and avoids repetition while maintaining clarity.
        """
        # Step 1: Generate an initial solution using a structured sequential approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying known quantities and unknowns. Then apply relevant formulas or logic step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "formulate_equations", "solve"]
        )

        # Step 2: First refinement pass using Review to catch errors and improve clarity
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass using Review again to polish reasoning and ensure completeness
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined