# Workflow ID: gsm8k_36_1
# Benchmark: gsm8k
# Data Indices: [996, 516]

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
        This is a diverse workflow using the Reflect-and-Regenerate pattern with Parallel Ensemble.
        It generates three solutions via FlexibleCustom with distinct reasoning styles, then uses
        reflection to guide refinement before final ensemble selection. This approach enhances robustness
        by incorporating meta-cognitive critique and iterative improvement.
        """
        # --- Step 1: Generate 3 diverse initial solutions using FlexibleCustom ---
        solution_list = []

        # Solution 1: Use branching logic — explore multiple interpretations of the problem structure
        sol1 = await self.flexible_custom(
            custom_instruction="Analyze possible interpretations of the scenario; resolve ambiguity through logical deduction.",
            reasoning_pattern="branching",
            steps=["identify_assumptions", "evaluate_consistency", "select_interpretation"]
        )

        # Solution 2: Use sequential logic — follow a strict step-by-step breakdown for clarity
        sol2 = await self.flexible_custom(
            custom_instruction="Break the problem into discrete, ordered steps: from inputs to final answer.",
            reasoning_pattern="sequential",
            steps=["gather_data", "formulate_plan", "execute_calculation", "validate_result"]
        )

        # Solution 3: Use iterative logic — start with a rough estimate and refine over time
        sol3 = await self.flexible_custom(
            custom_instruction="Begin with an intuitive guess, then improve through iterative checks and adjustments.",
            reasoning_pattern="iterative",
            steps=["initial_estimate", "check_accuracy", "refine"],
            max_iterations=2
        )

        solution_list.extend([sol1, sol2, sol3])

        # --- Step 2: Use Reflect on each solution to uncover potential flaws or assumptions ---
        reflected_solutions = []
        for sol in solution_list:
            reflection = await self.reflect(pre_solution=sol)
            # Use reflection to guide a new attempt — this mimics human metacognition
            improved_sol = await self.custom(
                instruction=f"Given the following reflection on the original solution: '{reflection}'. "
                           f"Now, generate a revised solution that addresses these concerns."
            )
            reflected_solutions.append(improved_sol)

        # --- Step 3: Use ScEnsemble to pick the most consistent and accurate solution from the improved set ---
        best_solution = await self.sc_ensemble(solutions=reflected_solutions)

        # --- Step 4: Final Review for clarity, completeness, and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer