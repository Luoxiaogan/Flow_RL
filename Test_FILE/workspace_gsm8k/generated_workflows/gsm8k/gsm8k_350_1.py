# Workflow ID: gsm8k_350_1
# Benchmark: gsm8k
# Data Indices: [416, 828, 455]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Robust parallel ensemble workflow using diverse reasoning strategies.
        This approach generates three distinct solutions via different reasoning patterns,
        then selects the most consistent one. A final review ensures clarity and correctness.
        """
        # Step 1: Generate multiple independent solutions using varied FlexibleCustom configurations
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential step-by-step (focus on breakdown)
                solution = await self.flexible_custom(
                    custom_instruction="Solve this math problem by breaking it into clear, sequential steps.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (start rough, improve)
                solution = await self.flexible_custom(
                    custom_instruction="Begin with an estimate, then refine your answer through iterative improvement.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Branching logic (consider alternatives)
                solution = await self.flexible_custom(
                    custom_instruction="Explore multiple possible interpretations or paths to solve this problem.",
                    reasoning_pattern="branching",
                    steps=["identify_paths", "evaluate", "choose_best"]
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish clarity and fix any lingering issues
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer