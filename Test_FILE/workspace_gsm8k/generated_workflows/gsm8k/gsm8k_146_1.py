# Workflow ID: gsm8k_146_1
# Benchmark: gsm8k
# Data Indices: [927, 642, 610]

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
        It generates 3 solutions via different reasoning strategies, then uses reflection to refine one of them.
        Finally, it ensembles all three to select the best answer — ensuring both diversity and meta-cognitive improvement.
        """
        # --- STEP 1: Generate 3 distinct solutions using FlexibleCustom with varied patterns ---
        solution_list = []

        # Solution 1: Iterative refinement (start rough, improve over iterations)
        sol1 = await self.flexible_custom(
            custom_instruction="Start with an initial estimate or guess. Then, iteratively refine your approach until you're confident in the result.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2
        )
        solution_list.append(sol1)

        # Solution 2: Parallel exploration (consider multiple interpretations at once)
        sol2 = await self.flexible_custom(
            custom_instruction="Explore multiple possible methods or perspectives simultaneously—e.g., algebraic, proportional, or visual reasoning.",
            reasoning_pattern="parallel",
            steps=["method_a", "method_b", "compare_results"]
        )
        solution_list.append(sol2)

        # Solution 3: Sequential logic (step-by-step breakdown without iteration)
        sol3 = await self.flexible_custom(
            custom_instruction="Break the problem into clear, sequential steps: identify knowns, unknowns, apply formulas, and verify the final answer.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"]
        )
        solution_list.append(sol3)

        # --- STEP 2: Use ScEnsemble to pick the most consistent and accurate solution from the three ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Reflect on the best solution to uncover hidden assumptions or errors ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate a new solution based on the reflection for improved accuracy ---
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection_text}'. Now, provide a refined and corrected version of the answer."
        )

        # --- STEP 5: Final review to ensure clarity, correctness, and completeness ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer