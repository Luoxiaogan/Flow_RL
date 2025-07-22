# Workflow ID: gsm8k_309_1
# Benchmark: gsm8k
# Data Indices: [200, 619]

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
        1. Generate 3 independent solutions via parallel execution (Fan-out).
        2. Use ScEnsemble to select the best solution.
        3. Critically reflect on that solution using Reflect operator.
        4. Regenerate a final improved solution based on the reflection (meta-cognitive loop).
        
        This combines:
        - Parallel Ensemble (for robustness and diversity of thought)
        - Reflect-and-Regenerate (for meta-cognition and targeted improvement)
        - Uses FlexibleCustom in sequential mode for structured reasoning in each branch
        """
        # Step 1: Generate multiple candidate solutions in parallel (fan-out)
        solution_candidates = []
        for i in range(3):
            # Each solution uses a different reasoning strategy via FlexibleCustom
            if i == 0:
                # Strategy 1: Step-by-step breakdown
                candidate = await self.flexible_custom(
                    custom_instruction="Break down the problem into clear steps.",
                    reasoning_pattern="sequential",
                    steps=["understand", "analyze", "solve", "verify"]
                )
            elif i == 1:
                # Strategy 2: Estimate-first then refine
                candidate = await self.flexible_custom(
                    custom_instruction="Start with rough estimates, then improve accuracy.",
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Consider alternative interpretations
                candidate = await self.flexible_custom(
                    custom_instruction="Explore multiple possible interpretations or approaches.",
                    reasoning_pattern="branching",
                    steps=["identify_assumptions", "explore_alternatives", "choose_best"]
                )
            solution_candidates.append(candidate)

        # Step 2: Select the best solution using ensemble evaluation
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect critically on the best solution — identify potential flaws, assumptions, or missed angles
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution using the reflection as guidance
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution:\n{reflection}\n\nNow, provide a revised and improved solution."
        )

        return final_solution