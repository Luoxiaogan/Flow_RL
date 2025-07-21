# Workflow ID: gsm8k_29_0
# Benchmark: gsm8k
# Data Indices: [140, 171]

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
        Generates 3 distinct solutions via varied reasoning strategies, then selects the best one.
        Final review ensures clarity and correctness.
        """
        # --- Step 1: Generate multiple independent solutions using different reasoning styles ---
        solution_list = []
        
        # Solution 1: Direct step-by-step breakdown (Sequential reasoning)
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "compute", "verify"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Parallel exploration of multiple interpretations (Parallel reasoning)
        par_solution = await self.flexible_custom(
            custom_instruction="Consider alternative ways to interpret the problem.",
            reasoning_pattern="parallel",
            steps=["interpretation_a", "interpretation_b", "compare"]
        )
        solution_list.append(par_solution)

        # Solution 3: Iterative refinement starting from estimation (Iterative reasoning)
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an estimate, then refine it through iterations.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "validate"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # --- Step 2: Use ScEnsemble to select the most consistent and accurate solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- Step 3: Final Review for polish and clarity ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer