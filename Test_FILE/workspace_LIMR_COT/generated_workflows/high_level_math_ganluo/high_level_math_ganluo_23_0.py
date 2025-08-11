# Workflow ID: high_level_math_ganluo_23_0
# Benchmark: high_level_math_ganluo
# Data Indices: [237, 243]

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

        # Step 1: Generate multiple initial solution strategies based on problem keywords
        strategies = await asyncio.gather(
            self.generate("Assume the polynomial has roots in arithmetic progression; derive conditions on a."),
            self.generate("Try substituting x = y + h to simplify the cubic equation."),
            self.generate("Explore whether complex roots imply specific symmetry in coefficients.")
        )

        # Step 2: Summarize each strategy to focus on key insights
        summaries = [await self.summarize(s) for s in strategies]

        # Step 3: Ensemble to identify common elements across approaches
        consensus = await self.ensemble(
            "Compare the three strategies and find the value of a that satisfies all constraints.",
            summaries
        )

        # Step 4: Revise if needed — check consistency with original problem constraints
        final_answer = await self.revise(
            "Verify that the proposed value of a leads to non-real roots forming an arithmetic progression.",
            consensus
        )

        return final_answer.strip()