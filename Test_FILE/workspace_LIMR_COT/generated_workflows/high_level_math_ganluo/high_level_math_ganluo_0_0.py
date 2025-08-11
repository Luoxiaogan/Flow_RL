# Workflow ID: high_level_math_ganluo_0_0
# Benchmark: high_level_math_ganluo
# Data Indices: [0, 579]

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

        # Step 1: Analyze problem type and constraints
        analysis = await self.generate("Identify key mathematical concepts, constraints, and potential solution methods in this problem.")

        # Step 2: Generate multiple candidate solution paths in parallel
        task1 = self.generate("Solve this using algebraic techniques.")
        task2 = self.generate("Approach this using geometric reasoning.")
        task3 = self.generate("Use combinatorial methods to solve.")
        task4 = self.generate("Apply number theory principles to find the solution.")

        results = await asyncio.gather(task1, task2, task3, task4)

        # Step 3: Summarize each candidate solution
        summaries = [await self.summarize(result) for result in results]

        # Step 4: Ensemble to select best solution
        final_answer = await self.ensemble(
            "Select the most mathematically sound and consistent solution based on the summaries.",
            summaries
        )

        # Optional: If ensemble result seems uncertain, refine it
        if "uncertain" in final_answer.lower() or "ambiguous" in final_answer.lower():
            refined = await self.revise(
                "Refine the solution by checking all constraints and verifying edge cases.",
                final_answer
            )
            final_answer = await self.ensemble(
                "Choose the most accurate version between the original and revised solution.",
                [final_answer, refined]
            )

        return final_answer