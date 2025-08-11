# Workflow ID: high_level_math_ganluo_15_0
# Benchmark: high_level_math_ganluo
# Data Indices: [22, 424]

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

        # Step 1: Diverge — generate multiple solution perspectives
        math_perspective = await self.generate(
            instruction="Generate an algebraic approach to solve this problem.",
            context=""
        )
        geo_perspective = await self.generate(
            instruction="Generate a geometric approach to solve this problem.",
            context=""
        )
        combinatorics_perspective = await self.generate(
            instruction="Generate a combinatorial approach to solve this problem.",
            context=""
        )

        # Step 2: Summarize each perspective to reduce noise and extract key ideas
        math_summary = await self.summarize(math_perspective)
        geo_summary = await self.summarize(geo_perspective)
        combinatorics_summary = await self.summarize(combinatorics_perspective)

        # Step 3: Converge — ensemble the summaries to get a unified candidate answer
        ensemble_response = await self.ensemble(
            instruction="Compare the three solution approaches and determine the most consistent and mathematically sound answer.",
            contexts_to_ensemble=[math_summary, geo_summary, combinatorics_summary]
        )

        # Step 4: Optional refinement — revise based on internal consistency or edge-case testing
        revised_answer = await self.revise(
            instruction="Check whether the proposed answer satisfies all constraints in the original problem. If not, refine it accordingly.",
            context_to_revise=ensemble_response
        )

        # Final output must be an integer between 0 and 999
        return revised_answer