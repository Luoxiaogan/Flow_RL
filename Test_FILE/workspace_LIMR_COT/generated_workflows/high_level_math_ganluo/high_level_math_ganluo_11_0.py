# Workflow ID: high_level_math_ganluo_11_0
# Benchmark: high_level_math_ganluo
# Data Indices: [590, 929]

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

        # Step 1: Initial analysis — understand the problem type
        initial_analysis = await self.generate(
            instruction="Identify the mathematical category of this problem (e.g., combinatorics, number theory, geometry, algebra, or mixed). Also list any explicit constraints or patterns mentioned."
        )

        # Step 2: Parallel exploration — generate 3 different solution strategies
        task1 = self.generate(
            instruction="Solve this problem using an algebraic approach, focusing on equations and variables."
        )
        task2 = self.generate(
            instruction="Solve this problem using a geometric approach, if applicable — consider coordinate geometry or synthetic methods."
        )
        task3 = self.generate(
            instruction="Solve this problem using a recursive or combinatorial method — look for patterns or counting structures."
        )

        # Execute all tasks in parallel
        results = await asyncio.gather(task1, task2, task3)

        # Step 3: Summarize each path for comparison
        summaries = [
            await self.summarize(context_to_summarize=results[0]),
            await self.summarize(context_to_summarize=results[1]),
            await self.summarize(context_to_summarize=results[2])
        ]

        # Step 4: Ensemble final decision — compare summaries and choose best answer
        final_answer = await self.ensemble(
            instruction="Compare the three solution summaries. Identify which one is most internally consistent, mathematically valid, and satisfies all constraints. Return only the integer answer between 0 and 999.",
            contexts_to_ensemble=summaries
        )

        return final_answer