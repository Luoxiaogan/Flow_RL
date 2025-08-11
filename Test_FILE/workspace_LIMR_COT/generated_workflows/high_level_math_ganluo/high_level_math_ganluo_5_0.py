# Workflow ID: high_level_math_ganluo_5_0
# Benchmark: high_level_math_ganluo
# Data Indices: [663, 92]

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

        # Step 1: Analyze problem type to guide strategy
        analysis = await self.generate(
            instruction="Identify the primary mathematical domain(s) involved in this problem (e.g., algebra, number theory, geometry). Be concise."
        )

        # Step 2: Generate three diverse solution approaches in parallel
        task1 = self.generate(
            instruction="Solve this problem directly using step-by-step algebraic manipulation or formula application."
        )
        task2 = self.generate(
            instruction="Model this as a recursive process or sequence. Solve by identifying base cases and recurrence relations."
        )
        task3 = self.generate(
            instruction="Look for symmetry, patterns, or invariants that simplify the problem. Use them to derive the solution."
        )

        results = await asyncio.gather(task1, task2, task3)

        # Step 3: Ensemble the three solutions to produce a final answer
        final_answer = await self.ensemble(
            instruction="Select the most consistent and mathematically sound answer among the three candidates. If they differ, explain why one is preferred.",
            contexts_to_ensemble=results
        )

        return final_answer