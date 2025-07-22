# Workflow ID: gsm8k_114_1
# Benchmark: gsm8k
# Data Indices: [400, 818, 419]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and efficient workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on it to identify potential flaws or improvements,
        then uses that reflection to guide a targeted re-solution — avoiding unnecessary complexity
        while ensuring metacognitive depth. This logic differs from the existing parallel ensemble
        by focusing on iterative insight over multiple solutions.
        """

        # Step 1: Generate an initial solution using structured reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear steps: identify knowns, unknowns, relationships, and compute.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "set_up_equations", "compute"]
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a corrected and improved answer."
        )

        return final_answer