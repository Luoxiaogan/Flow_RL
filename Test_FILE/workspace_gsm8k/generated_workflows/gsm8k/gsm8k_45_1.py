# Workflow ID: gsm8k_45_1
# Benchmark: gsm8k
# Data Indices: [491, 441]

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
        Reflect and Regenerate Workflow: 
        This pattern uses critical self-reflection to guide a superior solution.
        First, generate an initial solution. Then, reflect on it to identify weaknesses.
        Finally, use that reflection to craft a more accurate and robust answer.
        This mimics human metacognition — thinking about how you think — leading to deeper insight.
        """

        # Step 1: Generate an initial solution using general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into clear steps: identify knowns, apply operations, verify logic, then state the final answer."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        # This step surfaces hidden assumptions, gaps, or potential errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        # The reflection is used as context in the prompt for a fresh Custom call
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Now, solve the problem again with this critique in mind. Focus on clarity, completeness, and correctness."
        )

        return final_solution