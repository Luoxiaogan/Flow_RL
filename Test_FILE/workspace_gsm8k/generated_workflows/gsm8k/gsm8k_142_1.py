# Workflow ID: gsm8k_142_1
# Benchmark: gsm8k
# Data Indices: [440, 751, 626]

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
        Iterative Refinement with Reflective Guidance: 
        This workflow uses a meta-cognitive loop where each refinement is informed by a critical reflection.
        Unlike the existing workflow which applies generic reviews, this one explicitly uses reflection to guide improvements—ensuring deeper insight and avoiding superficial fixes.
        """
        # Step 1: Generate an initial solution using a structured sequential approach
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Solve the problem step-by-step, ensuring clarity and correctness in each stage."
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a revised solution — this is not just editing, but guided rethinking
        first_improved = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved reasoning."
        )

        # Step 4: Apply another round of reflection to further refine understanding
        second_reflection = await self.reflect(pre_solution=first_improved)

        # Step 5: Final refinement using the second reflection as a guide for a new solution
        final_solution = await self.custom(
            instruction=f"Using the reflection below, provide a final, polished answer: '{second_reflection}'"
        )

        return final_solution