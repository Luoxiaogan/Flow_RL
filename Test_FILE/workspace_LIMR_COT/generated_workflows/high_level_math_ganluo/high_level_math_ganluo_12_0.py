# Workflow ID: high_level_math_ganluo_12_0
# Benchmark: high_level_math_ganluo
# Data Indices: [382, 645]

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

        # Step 1: Diverge — Generate multiple solution strategies in parallel
        task1 = self.generate("Solve using algebraic manipulation: express variables in terms of each other.")
        task2 = self.generate("Solve using combinatorial reasoning: count valid configurations under constraints.")
        task3 = self.generate("Solve using coordinate geometry or synthetic geometry: apply spatial reasoning.")

        results = await asyncio.gather(task1, task2, task3)

        # Step 2: Converge — Summarize each approach to distill key reasoning
        summaries = [
            await self.summarize(results[0]),
            await self.summarize(results[1]),
            await self.summarize(results[2])
        ]

        # Step 3: Ensemble — Synthesize top candidate answers from summaries
        final_answer = await self.ensemble(
            "Choose the most consistent and mathematically sound answer from these three solution summaries.",
            summaries
        )

        # Step 4: Bidirectional Verification — Check if the answer satisfies original constraints
        verification_prompt = f"Given the answer {final_answer}, generate an inverse problem that should lead back to the original problem statement. Then verify if solving that inverse yields the same answer."
        verification_result = await self.generate(verification_prompt)

        # If verification fails, revise the final answer
        if "does not match" in verification_result.lower() or "invalid" in verification_result.lower():
            final_answer = await self.revise(
                "Revise the answer based on failed verification. Re-evaluate the solution steps for logical consistency.",
                final_answer
            )

        return final_answer