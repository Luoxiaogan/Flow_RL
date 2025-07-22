# Workflow ID: gsm8k_61_1
# Benchmark: gsm8k
# Data Indices: [172, 744]

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
        Diverse and robust workflow using Reflect-and-Regenerate with Parallel Ensemble.
        Generates 3 solutions via FlexibleCustom with different reasoning patterns.
        Uses Reflect to critique each solution before ensembling — a meta-cognitive loop.
        Final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple candidate solutions using varied reasoning strategies
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential: Clear, structured breakdown
                sol = await self.flexible_custom(
                    custom_instruction="Solve step-by-step by identifying knowns, unknowns, and applying logic.",
                    reasoning_pattern="sequential",
                    steps=["identify", "formulate", "compute", "verify"]
                )
            elif i == 1:
                # Iterative: Start rough, refine based on feedback
                sol = await self.flexible_custom(
                    custom_instruction="Begin with an estimate; improve through iterative refinement.",
                    reasoning_pattern="iterative",
                    steps=["initial_estimate", "improve", "validate"],
                    max_iterations=2
                )
            else:
                # Branching: Explore alternative interpretations or methods
                sol = await self.flexible_custom(
                    custom_instruction="Consider multiple possible ways to interpret the problem.",
                    reasoning_pattern="branching",
                    steps=["interpret", "compare", "select"]
                )
            solutions.append(sol)

        # Step 2: For each solution, apply Reflect to generate critical insights
        reflections = []
        for sol in solutions:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # Step 3: Use ScEnsemble not just on raw solutions, but on a hybrid of solutions + reflections
        # This introduces a novel ensemble strategy: evaluate both content and metacognition
        ensemble_input = [
            f"Solution: {sol}\nReflection: {refl}"
            for sol, refl in zip(solutions, reflections)
        ]
        
        best_solution_with_context = await self.sc_ensemble(solutions=ensemble_input)

        # Step 4: Final polish via Review to ensure clarity and correctness
        final_answer = await self.review(pre_solution=best_solution_with_context)

        return final_answer