# Workflow ID: gsm8k_279_0
# Benchmark: gsm8k
# Data Indices: [815, 261, 559]

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
        - Parallel Ensemble (fan-out/fan-in) for robustness
        - Reflect-and-Regenerate loop to incorporate meta-cognition
        - Iterative refinement via FlexibleCustom for deep reasoning
        """

        # Step 1: Generate multiple solutions in parallel using different strategies
        solution_pool = []
        strategies = [
            "Break the problem into smaller steps and solve each systematically.",
            "Use visual or spatial reasoning to model the scenario.",
            "Apply dimensional analysis to ensure unit consistency."
        ]
        
        for strategy in strategies:
            solution = await self.custom(instruction=f"{strategy}")
            solution_pool.append(solution)

        # Step 2: Use ScEnsemble to select the best initial solution
        best_initial = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect on the chosen solution — critique its assumptions, clarity, and logic
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Conditional logic based on reflection content
        # If reflection suggests uncertainty or missing elements, regenerate
        if "uncertain" in reflection.lower() or "missing" in reflection.lower():
            # Regenerate with guidance from reflection
            improved_solution = await self.custom(
                instruction=f"Based on the following reflection:\n{reflection}\n\nRe-solve the problem with more precision and attention to detail."
            )
        else:
            # Otherwise, use iterative refinement via FlexibleCustom
            improved_solution = await self.flexible_custom(
                custom_instruction="Refine the initial solution through structured iteration",
                reasoning_pattern="iterative",
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2
            )

        # Step 5: Final review to polish the answer
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer