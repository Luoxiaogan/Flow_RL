# Workflow ID: gsm8k_174_1
# Benchmark: gsm8k
# Data Indices: [781, 404]

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
        This is a diverse workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution and applies the Review operator twice
        to progressively improve the answer through structured feedback loops.
        This differs from the existing workflow by focusing on iterative refinement
        rather than reflection-guided regeneration, and avoids ensemble or branching logic.
        """
        # Step 1: Generate a basic, straightforward solution using a flexible custom operator
        # with a sequential reasoning pattern for clarity and structure
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step. Begin by identifying what is given and what needs to be found.",
            reasoning_pattern="sequential",
            steps=["identify_givens", "define_relationships", "set_up_equations", "compute_answer"]
        )

        # Step 2: Apply the Review operator once to improve the initial solution
        first_review = await self.review(pre_solution=initial_solution)

        # Step 3: Apply the Review operator a second time to further refine the solution
        second_review = await self.review(pre_solution=first_review)

        # Return the final refined solution after two rounds of review
        return second_review