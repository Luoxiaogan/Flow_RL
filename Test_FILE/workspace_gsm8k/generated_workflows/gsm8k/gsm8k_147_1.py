# Workflow ID: gsm8k_147_1
# Benchmark: gsm8k
# Data Indices: [270, 991]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate
        - First, generate 3 independent solutions in parallel (Parallel Ensemble pattern).
        - Then, select the best one using ScEnsemble.
        - Critically reflect on that best solution to identify potential flaws or improvements.
        - Finally, regenerate a new solution based on the reflection — this ensures meta-cognitive refinement (Reflect-and-Regenerate pattern).
        
        This approach combines robustness (multiple starting points) with deep critical thinking (reflection), creating a fundamentally different logic than iterative review alone.
        """

        # Step 1: Generate 3 diverse initial solutions using FlexibleCustom in parallel (each with unique reasoning steps)
        solution_prompts = [
            "Break down the problem into knowns and unknowns, then solve step-by-step.",
            "Solve by first estimating the answer, then computing precisely.",
            "Use dimensional analysis or unit-based reasoning to ensure correctness."
        ]
        solutions = []
        for prompt in solution_prompts:
            sol = await self.flexible_custom(
                custom_instruction=prompt,
                reasoning_pattern="sequential",
                steps=["identify", "plan", "execute", "validate"]
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — do not rewrite yet
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a completely new solution attempt
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Now, produce a revised and improved solution that addresses these concerns explicitly."
        )

        return final_answer