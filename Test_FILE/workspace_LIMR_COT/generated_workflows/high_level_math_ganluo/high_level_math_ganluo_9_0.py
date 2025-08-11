# Workflow ID: high_level_math_ganluo_9_0
# Benchmark: high_level_math_ganluo
# Data Indices: [836, 745]

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

        # Step 1: Extract and summarize key constraints
        summary = await self.summarize(self.problem_text)

        # Step 2: Generate multiple solution strategies in parallel
        task1 = self.generate("Solve using algebraic manipulation", context=summary)
        task2 = self.generate("Approach using number theory techniques", context=summary)
        task3 = self.generate("Try coordinate geometry if applicable", context=summary)
        task4 = self.generate("Explore combinatorial counting method", context=summary)

        # Execute all approaches in parallel
        results = await asyncio.gather(task1, task2, task3, task4)

        # Step 3: Refine each candidate solution with iterative revision
        revised_results = []
        for result in results:
            refined = await self.revise("Improve clarity and correctness of this solution", context_to_revise=result)
            revised_results.append(refined)

        # Step 4: Ensemble the top candidates into a single, robust answer
        final_answer = await self.ensemble(
            "Select the most consistent and mathematically sound answer from these options",
            contexts_to_ensemble=revised_results
        )

        return final_answer