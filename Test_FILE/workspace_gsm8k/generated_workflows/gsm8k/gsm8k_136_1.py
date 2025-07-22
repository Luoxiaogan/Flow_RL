# Workflow ID: gsm8k_136_1
# Benchmark: gsm8k
# Data Indices: [141, 388, 613]

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
        This is a diverse and robust workflow using:
        1. Iterative Refinement (via FlexibleCustom with iterative pattern)
        2. Reflect-and-Regenerate (using Reflect to critique and guide a new Custom call)
        
        The logic starts with an initial solution via FlexibleCustom in iterative mode.
        Then, it reflects on that solution, uses the reflection to generate a better one,
        and finally reviews the improved result for clarity and correctness.
        This structure introduces meta-cognition (reflection) and progressive improvement,
        differing fundamentally from the parallel ensemble approach in the existing workflow.
        """
        # Step 1: Use FlexibleCustom with iterative reasoning pattern for structured refinement
        iterative_solution = await self.flexible_custom(
            custom_instruction="Begin by estimating the answer, then refine step-by-step.",
            reasoning_pattern="iterative",
            steps=["estimate", "analyze", "refine", "verify"],
            max_iterations=3
        )

        # Step 2: Critically reflect on the iterative solution to uncover hidden assumptions or errors
        reflection_text = await self.reflect(pre_solution=iterative_solution)

        # Step 3: Generate a new, improved solution based on the reflection
        # This mimics human metacognition — learning from mistakes to improve
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the previous attempt: '{reflection_text}'. "
                        f"Use this insight to produce a more accurate and logically sound solution."
        )

        # Step 4: Final polish and clarity check via Review
        polished_answer = await self.review(pre_solution=final_solution)

        return polished_answer