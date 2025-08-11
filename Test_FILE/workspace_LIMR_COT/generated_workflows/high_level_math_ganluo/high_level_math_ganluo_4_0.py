# Workflow ID: high_level_math_ganluo_4_0
# Benchmark: high_level_math_ganluo
# Data Indices: [738, 187]

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

        # Step 1: Initial problem classification
        analysis = await self.generate("Identify the primary mathematical domain of this problem: algebra, geometry, number theory, combinatorics, or mixed.")

        # Step 2: Parallel exploration of different solution strategies
        task1 = self.generate("Solve using algebraic techniques such as simplification, factoring, or substitution.")
        task2 = self.generate("Solve using geometric reasoning or coordinate methods.")
        task3 = self.generate("Solve using number theory concepts like modular arithmetic, prime factorization, or Diophantine equations.")

        solutions = await asyncio.gather(task1, task2, task3)

        # Step 3: Summarize each solution path
        summaries = [await self.summarize(sol) for sol in solutions]

        # Step 4: Ensemble final answer based on consistency across methods
        final_answer = await self.ensemble(
            "Select the most consistent and mathematically sound answer from the following solution summaries. Prioritize clarity, logical coherence, and adherence to problem constraints.",
            summaries
        )

        return final_answer