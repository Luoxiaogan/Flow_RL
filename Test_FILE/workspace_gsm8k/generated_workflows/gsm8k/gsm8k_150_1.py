# Workflow ID: gsm8k_150_1
# Benchmark: gsm8k
# Data Indices: [443, 866, 408]

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
        This is a diverse and robust workflow using the Parallel Ensemble pattern.
        It generates three distinct solutions using different reasoning strategies via FlexibleCustom,
        then selects the most consistent one using ScEnsemble. Finally, it applies a single Review
        to polish the best solution — ensuring both diversity of thought and final quality.
        """
        # Step 1: Generate multiple independent solutions using varied reasoning patterns
        solution_list = []
        
        # Solution 1: Use sequential reasoning with clear step breakdown
        seq_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"],
            custom_instruction="Break down the problem into four logical stages: understand the question, analyze knowns and unknowns, solve step-by-step, and verify your answer."
        )
        solution_list.append(seq_solution)

        # Solution 2: Use iterative refinement to improve accuracy
        iter_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "finalize"],
            max_iterations=2,
            custom_instruction="Start with an initial estimate or approach, then refine it in at least one iteration before finalizing."
        )
        solution_list.append(iter_solution)

        # Solution 3: Use branching logic to explore alternative paths
        branch_solution = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["identify_path", "evaluate_options", "choose_best"],
            custom_instruction="Consider multiple possible approaches to solving this problem, evaluate each briefly, and choose the most promising path for detailed execution."
        )
        solution_list.append(branch_solution)

        # Step 2: Use ScEnsemble to select the most accurate and consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final review to ensure clarity, correctness, and completeness
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer