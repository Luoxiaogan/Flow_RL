# Benchmark: GSM8K
# Workflow ID: gsm8k_15
# Data Indices: [180, 181, 182]
# Generation Time: 2025-07-17 20:55:23
# Status: generated
# ==================================================

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
        self.reflect = operator.Reflect(self.config, self.problem) # New operator

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        # --- Diverse and effective workflow logic ---
        
        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the solution to identify potential issues or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new solution generation
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection: {reflection}. Re-evaluate the problem and provide a revised solution."
        )

        # Step 4: Review the improved solution for clarity, correctness, and completeness
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution