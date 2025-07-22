# Workflow ID: gsm8k_149_1
# Benchmark: gsm8k
# Data Indices: [464, 545]

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
        This is a diverse and efficient workflow using parallel ensemble with iterative refinement.
        It generates multiple initial solutions in parallel, then refines the best one — leveraging both diversity and depth.
        """
        # Step 1: Generate 3 independent solutions using flexible custom with different reasoning patterns
        solution1 = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Solve step-by-step, showing all calculations clearly."
        )
        
        solution2 = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "validate"],
            max_iterations=2,
            custom_instruction="Start with estimation, then refine for accuracy."
        )
        
        solution3 = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["identify_assumptions", "explore_alternatives", "choose_best"],
            custom_instruction="Consider multiple possible interpretations of the problem."
        )

        # Step 2: Use ScEnsemble to pick the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Review the best solution to improve clarity or fix subtle errors
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution