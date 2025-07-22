# Workflow ID: gsm8k_282_1
# Benchmark: gsm8k
# Data Indices: [574, 119]

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
        It first generates three solutions using different reasoning strategies (via FlexibleCustom),
        then uses reflection to critique each, and finally ensembles the best-performing one after refinement.
        This ensures both diversity in initial approaches and meta-cognitive improvement.
        """

        # --- STEP 1: Generate 3 distinct solutions using FlexibleCustom with varied patterns ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential: step-by-step breakdown
                instruction = "Solve by identifying all items, calculating each cost individually, then summing."
                flexible_op = self.flexible_custom(
                    reasoning_pattern="sequential",
                    steps=["identify_items", "calculate_individual_costs", "sum_total"],
                    custom_instruction=instruction
                )
            elif i == 1:
                # Iterative: start with estimation, refine
                instruction = "Begin with approximate values, then refine your calculation iteratively."
                flexible_op = self.flexible_custom(
                    reasoning_pattern="iterative",
                    steps=["estimate", "refine", "verify"],
                    max_iterations=2,
                    custom_instruction=instruction
                )
            else:
                # Branching: consider multiple interpretations or assumptions
                instruction = "Explore alternative ways to interpret the problem; choose the most logical path."
                flexible_op = self.flexible_custom(
                    reasoning_pattern="branching",
                    steps=["analyze_assumptions", "evaluate_options", "select_best"],
                    custom_instruction=instruction
                )

            solution = await flexible_op()
            solution_list.append(solution)

        # --- STEP 2: Use Reflect to generate critiques for each solution ---
        reflections = []
        for sol in solution_list:
            reflection = await self.reflect(pre_solution=sol)
            reflections.append(reflection)

        # --- STEP 3: Regenerate improved versions based on reflection ---
        refined_solutions = []
        for i, sol in enumerate(solution_list):
            improved_instruction = f"Based on this reflection: {reflections[i]}. Now re-solve the problem with clearer logic and fewer errors."
            improved_solution = await self.custom(instruction=improved_instruction)
            refined_solutions.append(improved_solution)

        # --- STEP 4: Ensembling - Select the most accurate and consistent solution from refined set ---
        best_solution = await self.sc_ensemble(solutions=refined_solutions)

        # --- FINAL STEP: Review for clarity and correctness ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer