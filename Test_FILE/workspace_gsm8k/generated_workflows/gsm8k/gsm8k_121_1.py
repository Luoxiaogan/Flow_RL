# Workflow ID: gsm8k_121_1
# Benchmark: gsm8k
# Data Indices: [795, 755, 981]

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
        Iterative Refinement with Meta-Cognitive Reflection: 
        This workflow uses a novel hybrid of iterative refinement and reflective critique.
        It generates an initial solution, then applies two rounds of refinement using the `review` operator.
        However, after the first review, it introduces a reflection step to analyze potential flaws before the second refinement — mimicking how humans improve by self-awareness.
        This creates a fundamentally different logic flow than simple iterative review: it adds a meta-cognitive layer between iterations.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Do not skip any steps."
        )

        # Step 2: First refinement - Improve clarity and correctness via review
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Reflect on the first refined solution — identify assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=first_refined)

        # Step 4: Second refinement — Use reflection to guide a new custom generation for deeper improvement
        second_refined = await self.custom(
            instruction=f"Based on the following reflection about the previous attempt: '{reflection}'. "
                        "Now, provide a revised and improved solution that addresses the identified issues while maintaining logical rigor."
        )

        return second_refined