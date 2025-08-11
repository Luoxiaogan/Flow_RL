# Workflow ID: high_level_math_ganluo_22_0
# Benchmark: high_level_math_ganluo
# Data Indices: [310, 459]

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

        # Step 1: Generate multiple solution paths in parallel
        task1 = self.generate("Solve using algebraic manipulation and equations.")
        task2 = self.generate("Approach using geometric interpretation and coordinate geometry.")
        task3 = self.generate("Analyze via combinatorial counting and case analysis.")
        task4 = self.generate("Use number theory techniques such as modular arithmetic or divisibility rules.")

        results = await asyncio.gather(task1, task2, task3, task4)

        # Step 2: Summarize each solution path to extract key insights
        summary1 = await self.summarize(results[0])
        summary2 = await self.summarize(results[1])
        summary3 = await self.summarize(results[2])
        summary4 = await self.summarize(results[3])

        summaries = [summary1, summary2, summary3, summary4]

        # Step 3: Ensemble the summaries to select the best-supported solution
        final_answer = await self.ensemble(
            "Select the most consistent and mathematically sound solution based on the following candidate approaches.",
            summaries
        )

        # Step 4: Optional revision if ensemble output lacks clarity or contains contradictions
        if "uncertain" in final_answer.lower() or "multiple" in final_answer.lower():
            final_answer = await self.revise(
                "Refine the solution to ensure it satisfies all constraints and provides a unique integer answer between 0 and 999.",
                final_answer
            )

        return final_answer