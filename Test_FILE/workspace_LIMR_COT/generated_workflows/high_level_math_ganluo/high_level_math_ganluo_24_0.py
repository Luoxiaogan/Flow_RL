# Workflow ID: high_level_math_ganluo_24_0
# Benchmark: high_level_math_ganluo
# Data Indices: [996, 210]

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

        # Step 1: Diverge — Generate multiple perspectives
        perspective1 = await self.generate("Identify key constraints and variables in the problem.")
        perspective2 = await self.generate("What mathematical domain does this belong to? (e.g., algebra, geometry, number theory)")
        perspective3 = await self.generate("List possible strategies based on common patterns in similar problems.")

        # Step 2: Converge — Summarize each perspective to extract structured insight
        summary1 = await self.summarize(perspective1)
        summary2 = await self.summarize(perspective2)
        summary3 = await self.summarize(perspective3)

        # Step 3: Ensemble — Synthesize into a single coherent plan
        synthesis = await self.ensemble(
            "Combine the three summaries to form a unified solution strategy.",
            [summary1, summary2, summary3]
        )

        # Optional: Refine the synthesis if it lacks clarity or specificity
        refined_plan = await self.revise(
            "Improve the plan by adding specific steps for handling edge cases and verifying the final answer.",
            synthesis
        )

        # Final step: Execute the refined plan using Generate to produce the actual answer
        final_answer = await self.generate(
            "Using the following solution strategy, compute the exact integer answer between 0 and 999:",
            context=refined_plan
        )

        return final_answer