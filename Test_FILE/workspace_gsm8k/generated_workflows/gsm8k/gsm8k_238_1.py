# Workflow ID: gsm8k_238_1
# Benchmark: gsm8k
# Data Indices: [698, 935, 415]

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
        Diverse workflow using Parallel Ensemble with structured reasoning patterns via FlexibleCustom.
        Step 1: Generate 3 distinct solutions using different reasoning strategies (sequential, iterative, branching).
        Step 2: Use ScEnsemble to select the most consistent and accurate solution.
        Step 3: Final Review for clarity, completeness, and logical flow — no regeneration needed.
        
        This differs from the existing workflow by:
        - Using FlexibleCustom with varied reasoning patterns instead of generic Custom calls
        - Applying ensemble *before* reflection or review (not after)
        - Avoiding reflective regeneration — instead focusing on initial diversity and final polish
        - Leveraging structured output from FlexibleCustom for better consistency across solutions
        """
        # --- STEP 1: Parallel Ensemble with Structured Reasoning Patterns ---
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential: step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Solve this math problem systematically.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "define_relationships", "formulate_equation", "compute"]
                )
            elif i == 1:
                # Iterative: start with estimate, refine
                solution = await self.flexible_custom(
                    custom_instruction="Begin with a rough estimate, then improve accuracy through refinement.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "check_consistency", "refine"],
                    max_iterations=2
                )
            else:
                # Branching: consider multiple paths, choose best
                solution = await self.flexible_custom(
                    custom_instruction="Explore alternative interpretations or methods. Choose the most logical path.",
                    reasoning_pattern="branching",
                    steps=["analyze_options", "evaluate_paths", "select_best"]
                )
            solution_list.append(solution)

        # --- STEP 2: Ensembling (Fan-in) ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final Review for Polish ---
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution