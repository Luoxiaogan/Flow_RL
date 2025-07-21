# Workflow ID: gsm8k_152_1
# Benchmark: gsm8k
# Data Indices: [97, 865, 745]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern with Parallel Ensemble.
        It generates three initial solutions via FlexibleCustom with different reasoning patterns (sequential, iterative, branching),
        then uses reflection to critique each, and finally selects the best one via ScEnsemble before a final review.
        This approach ensures both structural diversity and meta-cognitive refinement.
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different reasoning patterns
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential: Clear step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve this problem systematically by identifying knowns, unknowns, and applying operations in sequence.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "define_unknowns", "apply_operations", "compute_result"]
                )
            elif i == 1:
                # Iterative: Start with estimation, refine through passes
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an approximate solution, then iteratively improve it based on intermediate checks.",
                    reasoning_pattern="iterative",
                    steps=["initial_estimate", "validate", "refine"],
                    max_iterations=2
                )
            else:
                # Branching: Consider multiple paths or interpretations
                solution = await self.flexible_custom(
                    custom_instruction="Explore multiple logical approaches to solve this—e.g., algebraic, arithmetic, or visual modeling—and synthesize the best path.",
                    reasoning_pattern="branching",
                    steps=["analyze_options", "evaluate_paths", "select_best"]
                )
            solution_list.append(solution)

        # Step 2: Use Reflect to generate critiques for each solution
        reflections = []
        for sol in solution_list:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # Step 3: Regenerate improved versions using the reflections as guidance
        improved_solutions = []
        for i, sol in enumerate(solution_list):
            instruction = f"Based on the following reflection: {reflections[i]}. Now, provide a revised solution that addresses potential flaws or missing elements."
            improved = await self.custom(instruction=instruction)
            improved_solutions.append(improved)

        # Step 4: Use ScEnsemble to select the most accurate and consistent solution from the improved set
        best_solution = await self.sc_ensemble(solutions=improved_solutions)

        # Step 5: Final Review to polish clarity and correctness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer