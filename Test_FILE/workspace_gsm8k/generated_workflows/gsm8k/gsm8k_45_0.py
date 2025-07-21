# Workflow ID: gsm8k_45_0
# Benchmark: gsm8k
# Data Indices: [518, 539]

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
        Generates 3 independent solutions via FlexibleCustom with different patterns,
        then selects the best one using ScEnsemble, followed by a final review for refinement.
        """
        # Step 1: Generate 3 diverse solutions using FlexibleCustom with different reasoning patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Apply systematic step-by-step breakdown",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Use iterative approximation and verification",
            reasoning_pattern="iterative",
            steps=["initial_guess", "check_accuracy", "refine"],
            max_iterations=2
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Explore multiple possible interpretations before solving",
            reasoning_pattern="branching",
            steps=["identify_assumptions", "evaluate_options", "choose_path", "execute"]
        )

        # Step 2: Enforce robustness via parallel ensemble
        solutions = [solution1, solution2, solution3]
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to catch any lingering errors or inconsistencies
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer