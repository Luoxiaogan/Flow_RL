# Workflow ID: gsm8k_13_1
# Benchmark: gsm8k
# Data Indices: [739, 649, 62]

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
        This workflow uses iterative refinement with a novel twist: 
        it starts with a simple solution, then applies Review twice in sequence to progressively improve it.
        Unlike the existing workflow which uses a structured sequential pattern once, this one emphasizes repeated improvement through feedback loops.
        It avoids ensemble or branching logic entirely — focusing purely on deepening reasoning via successive reviews.
        """

        # Step 1: Generate an initial solution using a basic instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear and concise."
        )

        # Step 2: First review – catch obvious errors, clarify logic
        first_revision = await self.review(pre_solution=initial_solution)

        # Step 3: Second review – refine further based on the first revision
        second_revision = await self.review(pre_solution=first_revision)

        # Optional: Use Reflect to analyze why the solution improved (for meta-cognition)
        reflection = await self.reflect(pre_solution=second_revision)

        # Step 4: Final polish using a new Custom call guided by the reflection
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the previous attempt: '{reflection}'. "
                        "Now, provide a fully refined and accurate solution that addresses all insights from the reflection."
        )

        return final_solution