# Workflow ID: gsm8k_395_0
# Benchmark: gsm8k
# Data Indices: [131, 319, 569]

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
        Robust parallel ensemble workflow using diverse reasoning strategies.
        Generates 3 distinct solutions via different FlexibleCustom patterns,
        then selects the best one with ScEnsemble, followed by a final review.
        """
        # --- Step 1: Generate 3 diverse solutions using Parallel Ensemble pattern ---
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: break into clear steps
                solution = await self.flexible_custom(
                    custom_instruction="Use step-by-step logical decomposition.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "define_unknowns", "apply_relations", "compute_final"]
                )
            elif i == 1:
                # Iterative refinement: start rough, improve over passes
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimate, then refine iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "check_consistency", "adjust"],
                    max_iterations=2
                )
            else:
                # Branching logic: explore alternative interpretations
                solution = await self.flexible_custom(
                    custom_instruction="Consider multiple possible interpretations of the relationships.",
                    reasoning_pattern="branching",
                    steps=["analyze_assumptions", "explore_alternatives", "resolve_conflicts"]
                )
            solutions.append(solution)

        # --- Step 2: Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Final Review for polish and error-checking ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer