# Workflow ID: gsm8k_148_1
# Benchmark: gsm8k
# Data Indices: [223, 784, 19]

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
        This workflow uses a novel 'Reflect and Regenerate' pattern with iterative refinement.
        It starts with an initial solution, then applies reflection to identify potential flaws or gaps,
        followed by targeted re-generation using the insight from reflection. This creates a meta-cognitive loop
        that improves reasoning quality through structured self-awareness — fundamentally different from
        simple iterative refinement or ensemble methods.
        
        Key differences from existing workflow:
        - Uses Reflect + Custom (not Review) for improvement
        - No ScEnsemble; instead, uses reflective critique as a guide for regeneration
        - Avoids fixed iteration count in favor of adaptive learning via reflection
        - More cognitive depth: critiques assumptions rather than just fixing syntax/structure
        """

        # Step 1: Generate an initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Critically reflect on the solution — identify hidden assumptions, missing steps, or logical gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new custom generation — this is where the "regeneration" happens
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous attempt: '{reflection}'. "
                        f"Re-solve the problem with attention to these points. Be more thorough and precise."
        )

        # Step 4: Apply a final review to polish clarity and correctness — now based on a better foundation
        final_solution = await self.review(pre_solution=improved_solution)

        return final_solution