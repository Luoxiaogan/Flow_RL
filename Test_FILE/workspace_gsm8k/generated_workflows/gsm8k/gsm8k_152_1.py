# Workflow ID: gsm8k_152_1
# Benchmark: gsm8k
# Data Indices: [399, 246, 609]

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
        Reflect and Regenerate Workflow: Generate an initial solution, critically reflect on it to identify flaws or assumptions,
        then use that reflection to guide a new, improved solution. This meta-cognitive loop mimics how humans refine their thinking
        by analyzing their own reasoning — a powerful alternative to iterative refinement.
        
        Key differences from existing workflow:
        - Uses Reflect as a critical analysis step before regeneration (not just review)
        - No multiple reviews; instead, one deep reflection guides one final improvement
        - Avoids ensemble or parallelism — focuses on quality of single solution through introspection
        - Emphasizes metacognition over mechanical iteration
        """
        # Step 1: Generate an initial solution using clear, structured reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Do not skip any steps."
        )

        # Step 2: Critically reflect on the solution — identify potential weaknesses, hidden assumptions, or logical gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a superior final solution
        final_solution = await self.custom(
            instruction=f"Given the following initial solution and the reflection on its possible flaws: '{reflection}'. "
                        "Now, provide a new, improved solution that addresses these concerns while maintaining accuracy and clarity."
        )

        return final_solution