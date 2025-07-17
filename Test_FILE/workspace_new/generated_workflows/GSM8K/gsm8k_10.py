# Benchmark: GSM8K
# Workflow ID: gsm8k_10
# Data Indices: [130, 131, 132]
# Generation Time: 2025-07-17 20:55:22
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
        self.reflect = operator.Reflect(self.config, self.problem)

    async def run_workflow(self):
        """
        This workflow uses a Reflect-Regenerate pattern with a fallback to ScEnsemble for robustness.
        It first generates an initial solution, reflects on it, and then regenerates a better one.
        If the reflection suggests uncertainty, it falls back to an ensemble of solutions.
        """

        # Step 1: Generate an initial solution using Custom
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly.")

        # Step 2: Reflect on the initial solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new solution
        improved_instruction = f"Based on the following reflection: {reflection}. Provide a revised and improved solution."
        improved_solution = await self.custom(instruction=improved_instruction)

        # Step 4: Optional - If the reflection indicates ambiguity or multiple interpretations,
        # generate multiple solutions and use ScEnsemble to pick the best one
        if "uncertain" in reflection.lower() or "alternative" in reflection.lower():
            solution_list = [
                await self.custom(instruction="Solve the problem from a different perspective."),
                await self.custom(instruction="Provide a solution using a more formal mathematical approach.")
            ]
            final_solution = await self.sc_ensemble(solutions=solution_list)
        else:
            final_solution = improved_solution

        return final_solution