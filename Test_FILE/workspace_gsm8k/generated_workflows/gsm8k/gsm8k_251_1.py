# Workflow ID: gsm8k_251_1
# Benchmark: gsm8k
# Data Indices: [268, 176, 446]

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
        1. Generate 3 independent solutions in parallel using FlexibleCustom with 'parallel' pattern.
        2. Use ScEnsemble to select the best solution.
        3. Critically reflect on that best solution using the new Reflect operator.
        4. Regenerate a final improved solution based on the reflection — mimicking human meta-cognition.
        
        This combines:
        - Parallel Ensemble (fan-out/fan-in) for robustness
        - Reflect-and-Regenerate (meta-cognitive loop) for deep refinement
        
        It's fundamentally different from the iterative Review-only approach:
        - Uses ensemble selection before refinement
        - Leverages structured reflection as a guide rather than just re-writing
        - Avoids multiple sequential reviews which can overfit to initial errors
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom in parallel mode
        # Each will use a slightly different reasoning strategy via steps list
        solutions = []
        strategies = [
            {"steps": ["analyze", "plan", "solve", "verify"]},
            {"steps": ["break_down", "model", "compute", "check"]},
            {"steps": ["identify_knowns", "formulate_equation", "solve", "validate"]}
        ]
        
        for i in range(3):
            fc = self.flexible_custom(
                reasoning_pattern="parallel",
                steps=strategies[i]["steps"],
                custom_instruction="Solve this math problem by following the given steps."
            )
            solution = await fc
            solutions.append(solution)

        # Step 2: Select the best solution using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the selected solution — identify flaws, assumptions, or missed angles
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a fresh, targeted Custom call for final improvement
        final_answer = await self.custom(
            instruction=f"Based on the following reflection on the previous solution:\n{reflection}\n\n"
                       f"Re-solve the problem with improved clarity, addressing potential weaknesses identified above."
        )

        return final_answer