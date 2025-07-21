# Workflow ID: gsm8k_80_1
# Benchmark: gsm8k
# Data Indices: [787, 199, 332]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on its potential flaws, and then uses that insight to produce a refined solution.
        Finally, it performs a review for clarity and correctness — ensuring both depth and polish.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Apply systematic problem decomposition: break the problem into knowns, unknowns, and operations.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_unknowns", "apply_operations", "combine_results"]
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        improved_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a revised solution that addresses these points."
        )

        # Step 4: Perform a final review to enhance clarity, structure, and correctness
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer