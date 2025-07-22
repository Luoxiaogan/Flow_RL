# Workflow ID: gsm8k_29_1
# Benchmark: gsm8k
# Data Indices: [423, 599, 65]

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
        Diverse and robust workflow using Parallel Ensemble + Iterative Refinement.
        1. Generate 3 diverse solutions via FlexibleCustom with different reasoning patterns (sequential, branching, iterative).
        2. Use ScEnsemble to select the most consistent solution from the three.
        3. Apply a final Review to polish the selected solution — not just fix errors, but improve clarity and structure.
        This design ensures both diversity in approach (parallel) and depth in refinement (iterative), making it more resilient than single-path methods.
        
        Key differences from existing:
        - Uses FlexibleCustom with distinct reasoning patterns instead of simple custom calls.
        - No reflection-based regeneration; instead, uses structured review after ensemble for final polish.
        - Ensembles first, then refines — unlike existing which reflects before regenerating.
        """

        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different strategies
        solutions = []
        patterns = ["sequential", "branching", "iterative"]
        instructions = [
            "Solve step-by-step with clear breakdowns.",
            "Consider multiple logical paths based on assumptions.",
            "Start with an estimate, then refine iteratively."
        ]

        for i in range(3):
            sol = await self.flexible_custom(
                custom_instruction=instructions[i],
                reasoning_pattern=patterns[i],
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if patterns[i] == "iterative" else 1
            )
            solutions.append(sol)

        # Step 2: Select the best solution using ScEnsemble (robustness via consensus)
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final refinement via Review — improves clarity, logic flow, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer