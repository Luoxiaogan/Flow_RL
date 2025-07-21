# Workflow ID: gsm8k_121_0
# Benchmark: gsm8k
# Data Indices: [706, 175, 948]

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
        Robust parallel ensemble workflow with iterative refinement and final review.
        Generates 3 diverse solutions using different reasoning patterns via FlexibleCustom,
        then selects the best one using ScEnsemble. Finally, applies a critical review for robustness.
        """
        # Step 1: Generate 3 diverse solutions using different reasoning strategies
        solution_list = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: step-by-step breakdown
                solution = await self.flexible_custom(
                    custom_instruction="Break the problem into clear steps: identify knowns, unknowns, apply logic, verify.",
                    reasoning_pattern="sequential",
                    steps=["identify_knowns", "identify_unknowns", "apply_logic", "verify"]
                )
            elif i == 1:
                # Iterative refinement: start with rough estimate, refine
                solution = await self.flexible_custom(
                    custom_instruction="Start with an initial guess, then improve through iterative steps.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Parallel approach: consider multiple interpretations
                solution = await self.flexible_custom(
                    custom_instruction="Explore multiple possible interpretations or solution paths simultaneously.",
                    reasoning_pattern="parallel",
                    steps=["interpretation_1", "interpretation_2", "choose_best"]
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final critical reflection and optional review for robustness
        reflection = await self.reflect(pre_solution=best_solution)
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution