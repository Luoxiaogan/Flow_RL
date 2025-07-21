# Workflow ID: gsm8k_95_1
# Benchmark: gsm8k
# Data Indices: [648, 279]

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
        This workflow uses the 'Reflect and Regenerate' pattern in a novel way:
        - First, generate an initial solution using a branching reasoning pattern.
        - Then, reflect on it to uncover hidden assumptions or errors.
        - Finally, use that reflection to guide a completely new custom solution — not just a refinement.
        
        This avoids iterative loops and instead leverages meta-cognition to produce a superior final answer.
        """
        # Step 1: Use FlexibleCustom with a branching pattern to explore multiple logical paths
        # This mimics how humans might approach problems by considering different strategies
        initial_solution = await self.flexible_custom(
            reasoning_pattern="branching",
            steps=["analyze", "consider_alternatives", "choose_best_path", "execute"],
            custom_instruction="Explore at least two distinct approaches to solving this problem. For each, outline your reasoning, then select the most promising one."
        )

        # Step 2: Critically reflect on the initial solution — focus on assumptions, logic gaps, and potential missteps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to construct a fresh, improved solution from scratch
        # Instead of refining, we regenerate based on insights — this is more powerful than iterative review
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                       f"Generate a completely new solution, ensuring all assumptions are validated and any flaws identified are addressed. "
                       f"Do not reuse the structure of the previous attempt; think critically and independently."
        )

        return final_solution