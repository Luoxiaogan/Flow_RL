# Workflow ID: high_level_math_ganluo_27_0
# Benchmark: high_level_math_ganluo
# Data Indices: [907, 329]

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

        # Step 1: Initial analysis to detect domain and potential strategies
        analysis = await self.generate(
            instruction="What mathematical domain(s) does this problem belong to? Suggest possible solution techniques based on the given constraints."
        )

        # Step 2: Diverge into three parallel solution paths
        task1 = self.generate(
            instruction="Solve using algebraic methods: translate the problem into equations, apply known formulas, and compute step-by-step."
        )
        task2 = self.generate(
            instruction="Solve using structural insight: look for symmetry, invariants, or recursive relationships that simplify the problem."
        )
        task3 = self.generate(
            instruction="Solve using number-theoretic or modular arithmetic: identify integer constraints, divisibility rules, or congruences that must hold."
        )

        # Execute all tasks in parallel
        solutions = await asyncio.gather(task1, task2, task3)

        # Step 3: Summarize each solution to extract key steps and assumptions
        summaries = [
            await self.summarize(context_to_summarize=sol)
            for sol in solutions
        ]

        # Step 4: Ensemble the summaries to select the most coherent and consistent answer
        final_answer = await self.ensemble(
            instruction="Based on the three solution summaries, determine the correct integer answer between 0 and 999. Resolve discrepancies by choosing the most mathematically consistent result.",
            contexts_to_ensemble=summaries
        )

        return final_answer