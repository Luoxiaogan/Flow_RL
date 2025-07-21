# Workflow ID: gsm8k_31_1
# Benchmark: gsm8k
# Data Indices: [192, 984, 756]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate.
        1. Generate 3 independent solutions using parallel reasoning (fan-out).
        2. Use ScEnsemble to select the best candidate.
        3. Reflect on that solution to identify weaknesses or alternative approaches.
        4. Regenerate a final improved solution based on reflection.
        
        This combines robustness (parallel) with meta-cognition (reflect) for higher-quality outcomes.
        """
        # Step 1: Generate multiple diverse initial solutions in parallel
        solutions = []
        for _ in range(3):
            sol = await self.flexible_custom(
                custom_instruction="Solve the problem using a unique approach—e.g., visual representation, step-by-step breakdown, or formula-based method.",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solutions.append(sol)

        # Step 2: Select the strongest solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected solution to uncover blind spots
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, refined solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. Now, provide a fully revised and improved answer."
        )

        return final_answer