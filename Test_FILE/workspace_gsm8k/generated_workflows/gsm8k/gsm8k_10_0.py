# Workflow ID: gsm8k_10_0
# Benchmark: gsm8k
# Data Indices: [177, 874, 318]

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
        It generates 3 different solutions via varied reasoning strategies,
        then selects the best one using ensemble evaluation, followed by a final review.
        """
        # Step 1: Generate multiple independent solutions using different reasoning patterns
        solution_list = []
        
        # Solution 1: Sequential decomposition (clear step-by-step breakdown)
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and solve each logically.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Iterative refinement (start with estimate, then improve)
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an initial estimate, then refine it through logical checks.",
            reasoning_pattern="iterative",
            steps=["estimate", "check", "refine"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Solution 3: Parallel approach (consider multiple interpretations or methods)
        parallel_solution = await self.flexible_custom(
            custom_instruction="Explore alternative ways to interpret the problem and solve it from different angles.",
            reasoning_pattern="parallel",
            steps=["interpret", "evaluate", "compare"]
        )
        solution_list.append(parallel_solution)

        # Step 2: Use ScEnsemble to select the most consistent and accurate solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review for polish and clarity — ensures output is well-articulated
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer