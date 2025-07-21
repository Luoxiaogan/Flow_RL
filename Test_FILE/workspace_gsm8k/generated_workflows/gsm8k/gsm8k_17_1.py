# Workflow ID: gsm8k_17_1
# Benchmark: gsm8k
# Data Indices: [719, 112, 254]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates three independent solutions with different reasoning strategies,
        then uses ScEnsemble to select the most consistent and accurate one.
        A final review step ensures clarity and correctness before returning the result.
        """
        # Step 1: Generate multiple solutions using parallel approaches
        solution_list = []
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential breakdown (like solving a puzzle step by step)
                solution = await self.flexible_custom(
                    custom_instruction="Break the problem into logical steps and solve each part systematically.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (start simple, improve iteratively)
                solution = await self.flexible_custom(
                    custom_instruction="Start with an initial estimate, then refine it through multiple passes.",
                    reasoning_pattern="iterative",
                    steps=["initial_guess", "refine", "final_answer"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Branching logic (consider alternative interpretations or paths)
                solution = await self.flexible_custom(
                    custom_instruction="Consider multiple possible interpretations of the problem and evaluate each.",
                    reasoning_pattern="branching",
                    steps=["identify_interpretations", "evaluate_options", "choose_best"]
                )
            solution_list.append(solution)

        # Step 2: Use ensemble to pick the best solution based on consistency and accuracy
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to polish and ensure clarity — adds robustness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer