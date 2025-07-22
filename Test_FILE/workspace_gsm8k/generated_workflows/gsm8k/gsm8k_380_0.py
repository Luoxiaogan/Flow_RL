# Workflow ID: gsm8k_380_0
# Benchmark: gsm8k
# Data Indices: [927, 468]

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
        Generates 3 different solutions via varied reasoning approaches, then ensembles them.
        A final review step ensures clarity and correctness.
        """
        # --- STEP 1: Generate 3 independent solutions using different strategies ---
        solution_list = []
        
        # Solution 1: Use FlexibleCustom with sequential reasoning (step-by-step decomposition)
        seq_solution = await self.flexible_custom(
            custom_instruction="Break the problem into clear logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )
        solution_list.append(seq_solution)

        # Solution 2: Use FlexibleCustom with iterative refinement
        iter_solution = await self.flexible_custom(
            custom_instruction="Start with an initial estimate, then refine it through multiple iterations.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "evaluate", "improve"],
            max_iterations=2
        )
        solution_list.append(iter_solution)

        # Solution 3: Use standard Custom with a creative angle — assume a value to test consistency
        creative_solution = await self.custom(
            instruction="Assume a total quantity, solve for that assumption, and verify if it leads to consistent results."
        )
        solution_list.append(creative_solution)

        # --- STEP 2: Enforce robustness by selecting the best solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Final quality check with Review to polish the output ---
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer