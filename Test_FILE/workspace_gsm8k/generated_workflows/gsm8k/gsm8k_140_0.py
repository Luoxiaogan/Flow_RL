# Workflow ID: gsm8k_140_0
# Benchmark: gsm8k
# Data Indices: [509, 886, 492]

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
        Generates 3 independent solutions via varied reasoning strategies, then selects the best one.
        A final review ensures clarity and correctness.
        """
        # Step 1: Generate 3 different solutions using distinct approaches
        solution_list = []
        
        # Solution 1: Use iterative refinement with FlexibleCustom (step-by-step breakdown)
        sol1 = await self.flexible_custom(
            custom_instruction="Solve this math problem by breaking it into clear steps.",
            reasoning_pattern="sequential",
            steps=["understand", "identify", "calculate", "verify"]
        )
        
        # Solution 2: Use parallel thinking — simulate multiple perspectives via Custom
        sol2 = await self.custom(instruction="Solve this problem as if you're explaining it to a student who needs clear, logical steps.")
        
        # Solution 3: Use another FlexibleCustom instance with an iterative pattern for refinement
        sol3 = await self.flexible_custom(
            custom_instruction="Start with an estimate, then refine your answer through logical checks.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "validate"],
            max_iterations=2
        )

        solution_list.extend([sol1, sol2, sol3])

        # Step 2: Enforce consistency using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Final Review for polish and error-checking
        final_answer = await self.review(pre_solution=best_solution)

        return final_answer