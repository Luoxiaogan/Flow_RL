# Workflow ID: high_level_math_ganluo_6_0
# Benchmark: high_level_math_ganluo
# Data Indices: [719, 55]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem # Assumes problem is a pre-processed string
        self.llm = create(config)

        # All available operators are initialized here for your use.
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        This is where you implement the core problem-solving logic.
        You can use any of the operators initialized above.
        """
        import asyncio

        # Step 1: Diverge — Generate three distinct solution strategies
        algebraic_approach = await self.generate(
            "Analyze this problem using algebraic methods such as substitution, expansion, or identity matching."
        )
        combinatorial_approach = await self.generate(
            "Consider if this problem involves counting, probability, recursion, or modular arithmetic."
        )
        geometric_approach = await self.generate(
            "If applicable, interpret this problem geometrically using coordinates, symmetry, or transformations."
        )

        # Step 2: Extract key ideas from each approach
        summary_a = await self.summarize(algebraic_approach)
        summary_c = await self.summarize(combinatorial_approach)
        summary_g = await self.summarize(geometric_approach)

        # Step 3: Converge — Ensemble the three summaries to find the best answer
        final_answer = await self.ensemble(
            "Compare these three solution paths and determine which provides the most consistent, mathematically sound answer. If there is disagreement, prioritize the one that satisfies all given constraints.",
            [summary_a, summary_c, summary_g]
        )

        return final_answer