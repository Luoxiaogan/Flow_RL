# Workflow ID: gsm8k_229_0
# Benchmark: gsm8k
# Data Indices: [214, 403, 3]

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
        This is a diverse and complex workflow combining:
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect-and-Regenerate pattern: critique the best solution, then use reflection to guide a new attempt
        3. Iterative Refinement: if the regenerated solution still has flaws, refine it further
        """

        # Step 1: Generate 3 independent solutions using Custom (Parallel Ensemble)
        solutions = []
        for i in range(3):
            instruction = "Solve the problem step-by-step using a different reasoning approach each time."
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # Step 2: Use ScEnsemble to select the best solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the best solution — identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a new solution that addresses the identified issues
        improved_instruction = f"Given the following reflection on the previous solution: '{reflection}'. Now, provide a revised solution that corrects any errors or assumptions found."
        final_solution = await self.custom(instruction=improved_instruction)

        # Step 5: Optional iterative refinement — if reflection suggests deeper issues, apply Review
        # This uses a conditional check based on the content of the reflection (e.g., if it mentions ambiguity, error, etc.)
        if "error" in reflection.lower() or "assumption" in reflection.lower() or "flaw" in reflection.lower():
            final_solution = await self.review(pre_solution=final_solution)

        return final_solution