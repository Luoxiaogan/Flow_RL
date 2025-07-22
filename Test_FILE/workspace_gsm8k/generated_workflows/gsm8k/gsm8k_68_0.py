# Workflow ID: gsm8k_68_0
# Benchmark: gsm8k
# Data Indices: [677, 825]

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
        Diverse and robust workflow using Parallel Ensemble with iterative refinement.
        Generates 3 independent solutions via FlexibleCustom with different reasoning patterns,
        then ensembles the best one. Final review ensures clarity and correctness.
        """
        # Step 1: Generate 3 diverse solutions using different reasoning strategies
        solutions = []
        for i in range(3):
            if i == 0:
                # Sequential reasoning: break down into clear steps
                solution = await self.flexible_custom(
                    custom_instruction="Use a step-by-step approach to solve math problems.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Iterative refinement: start rough, improve iteratively
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an initial estimate, then refine through multiple iterations.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "validate"],
                    max_iterations=2
                )
            else:
                # Branching logic: explore multiple paths based on intermediate results
                solution = await self.flexible_custom(
                    custom_instruction="Consider alternative interpretations or methods to solve the problem.",
                    reasoning_pattern="branching",
                    steps=["identify_approaches", "evaluate_options", "choose_best"]
                )
            solutions.append(solution)

        # Step 2: Use ScEnsemble to pick the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to polish clarity and fix any lingering issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer