# Workflow ID: gsm8k_39_1
# Benchmark: gsm8k
# Data Indices: [12, 401]

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
        Diverse and robust workflow using Parallel Ensemble with Reflect-based refinement.
        Generates 3 solutions via distinct reasoning styles (deductive, inductive, analogical).
        Uses reflection to critique each solution before ensembling — enhancing consistency.
        Final review ensures clarity and correctness.
        """

        # Step 1: Generate three diverse solutions using FlexibleCustom with different patterns
        solutions = []

        # Solution 1: Deductive approach — start from known facts and logically derive the answer
        sol1 = await self.flexible_custom(
            custom_instruction="Use deductive logic: begin with what is explicitly given and build step-by-step.",
            reasoning_pattern="sequential",
            steps=["extract_facts", "apply_rules", "compute_result", "validate"]
        )

        # Solution 2: Inductive approach — observe patterns and generalize from partial data
        sol2 = await self.flexible_custom(
            custom_instruction="Apply inductive reasoning: look for patterns or relationships that suggest a general rule.",
            reasoning_pattern="iterative",
            steps=["identify_pattern", "form_hypothesis", "test_with_examples", "refine"],
            max_iterations=2
        )

        # Solution 3: Analogical approach — map the problem to a similar one you’ve solved before
        sol3 = await self.flexible_custom(
            custom_instruction="Solve by analogy: think of a similar problem structure and apply its method here.",
            reasoning_pattern="parallel",
            steps=["find_similar_problem", "adapt_strategy", "adjust_for_differences", "apply"]
        )

        solutions.extend([sol1, sol2, sol3])

        # Step 2: For each solution, generate a reflection to identify potential flaws
        reflections = []
        for sol in solutions:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # Step 3: Use ScEnsemble to select the most consistent solution based on raw outputs
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Final Review to polish the selected solution
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer