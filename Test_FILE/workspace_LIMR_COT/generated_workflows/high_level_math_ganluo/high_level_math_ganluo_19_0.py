# Workflow ID: high_level_math_ganluo_19_0
# Benchmark: high_level_math_ganluo
# Data Indices: [597, 608]

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

        # Step 1: Initial analysis — determine problem type and key constraints
        analysis = await self.generate(
            instruction="Identify the category of this math problem (combinatorics, number theory, geometry, algebra, etc.) and list its main constraints.",
            context=""
        )

        # Step 2: Parallel exploration — generate 3 different solution strategies
        task1 = self.generate(
            instruction="Propose an algebraic solution path based on the constraints and expression structure.",
            context=analysis
        )
        task2 = self.generate(
            instruction="Propose a geometric or coordinate-based interpretation if applicable.",
            context=analysis
        )
        task3 = self.generate(
            instruction="Propose a number-theoretic or combinatorial approach if the problem involves integers or counting.",
            context=analysis
        )

        solutions = await asyncio.gather(task1, task2, task3)

        # Step 3: Refine each candidate solution for correctness and clarity
        revised_solutions = []
        for sol in solutions:
            refined = await self.revise(
                instruction="Improve this solution draft by checking for logical gaps, missing assumptions, or calculation errors.",
                context_to_revise=sol
            )
            revised_solutions.append(refined)

        # Step 4: Ensemble final decision — pick the most coherent and accurate answer
        final_answer = await self.ensemble(
            instruction="Evaluate the three proposed solutions and return the one that best satisfies all constraints and mathematical principles.",
            contexts_to_ensemble=revised_solutions
        )

        return final_answer