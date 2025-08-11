# Workflow ID: high_level_math_ganluo_31_0
# Benchmark: high_level_math_ganluo
# Data Indices: [189, 514]

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

        # Step 1: Generate 3 diverse solution strategies in parallel
        task1 = self.generate("Solve this using algebraic methods.")
        task2 = self.generate("Solve this using geometric reasoning.")
        task3 = self.generate("Solve this using combinatorial or number-theoretic methods.")

        # Execute all in parallel
        solutions = await asyncio.gather(task1, task2, task3)

        # Step 2: Summarize each solution path
        summary1 = await self.summarize(solutions[0])
        summary2 = await self.summarize(solutions[1])
        summary3 = await self.summarize(solutions[2])

        # Step 3: Ensemble the summaries to find consensus
        ensemble_result = await self.ensemble(
            "Compare these three solution summaries and identify the most consistent answer.",
            [summary1, summary2, summary3]
        )

        # Step 4: Revise the ensemble result by checking against original constraints
        final_answer = await self.revise(
            "Verify that the proposed answer satisfies all constraints in the original problem statement.",
            ensemble_result
        )

        # Step 5: Return the final refined answer
        return final_answer