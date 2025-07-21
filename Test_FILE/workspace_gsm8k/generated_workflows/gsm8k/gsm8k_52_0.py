# Workflow ID: gsm8k_52_0
# Benchmark: gsm8k
# Data Indices: [627, 193]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates three independent solutions via varied reasoning strategies,
        then selects the best one using ensemble evaluation, followed by a final review.
        """
        # Step 1: Generate 3 diverse solutions using different FlexibleCustom configurations
        solution_list = []
        
        for i in range(3):
            if i == 0:
                # Strategy 1: Sequential breakdown (analyze → plan → solve → verify)
                solution = await self.flexible_custom(
                    custom_instruction="Break down the problem step-by-step with clear reasoning.",
                    reasoning_pattern="sequential",
                    steps=["analyze", "plan", "solve", "verify"]
                )
            elif i == 1:
                # Strategy 2: Iterative refinement (start simple, then improve)
                solution = await self.flexible_custom(
                    custom_instruction="Start with an estimation, then refine your approach iteratively.",
                    reasoning_pattern="iterative",
                    steps=["initial_approach", "refine", "finalize"],
                    max_iterations=2
                )
            else:
                # Strategy 3: Branching logic based on intermediate checks
                solution = await self.flexible_custom(
                    custom_instruction="Use conditional reasoning to explore multiple paths.",
                    reasoning_pattern="branching",
                    steps=["identify_knowns", "consider_alternatives", "choose_best_path", "calculate"]
                )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review for polish and clarity
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer