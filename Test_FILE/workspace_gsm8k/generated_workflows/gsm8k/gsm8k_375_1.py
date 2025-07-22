# Workflow ID: gsm8k_375_1
# Benchmark: gsm8k
# Data Indices: [585, 844]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it to uncover hidden flaws or missed steps,
        and finally uses that reflection to guide a new, improved solution. This mimics human meta-cognition:
        think → evaluate → improve.
        
        Key differences from the existing workflow:
        - No iterative refinement (no multiple reviews); instead, one deep reflection guides a single regeneration.
        - Uses Reflect as a critical thinking engine, not just a diagnostic tool — its output directly shapes the next step.
        - Avoids ensemble methods entirely; focuses on quality of reasoning over quantity of attempts.
        - Emphasizes structured reflection before generating a final answer — a novel logic flow compared to simple fix-and-repeat.
        """

        # Step 1: Generate an initial solution with clear, step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into parts, show your work clearly, and state the final answer."
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, logical gaps, or ambiguity
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined, higher-quality solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection on the previous solution: '{reflection}'. Now, provide a revised answer that addresses all concerns raised above. Be precise, complete, and logically sound."
        )

        return final_solution