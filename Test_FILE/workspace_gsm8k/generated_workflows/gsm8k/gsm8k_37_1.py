# Workflow ID: gsm8k_37_1
# Benchmark: gsm8k
# Data Indices: [118, 517, 457]

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
        This is a diverse and efficient workflow using a parallel ensemble strategy.
        It generates three independent solutions using the FlexibleCustom operator with different reasoning patterns,
        then selects the best one via ScEnsemble. This approach leverages multiple reasoning styles (sequential, iterative, branching)
        to increase robustness without overcomplicating the logic — ideal for efficiency and accuracy.
        """
        # Step 1: Generate three diverse solutions using different reasoning patterns
        sequential_solution = await self.flexible_custom(
            custom_instruction="Solve this step-by-step in a linear fashion.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        iterative_solution = await self.flexible_custom(
            custom_instruction="Start with an estimate, then refine through iterations.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2
        )

        branching_solution = await self.flexible_custom(
            custom_instruction="Consider multiple possible interpretations or paths.",
            reasoning_pattern="branching",
            steps=["identify_options", "evaluate", "choose_best"]
        )

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        final_solution = await self.sc_ensemble(solutions=[sequential_solution, iterative_solution, branching_solution])

        return final_solution