# Workflow ID: high_level_math_ganluo_1_0
# Benchmark: high_level_math_ganluo
# Data Indices: [679, 426]

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

        # Step 1: Initial analysis to determine likely solution method
        initial_analysis = await self.generate(
            instruction="Identify the mathematical category of this problem (e.g., combinatorics, number theory, geometry, algebra). Suggest at least three possible solution strategies."
        )

        # Step 2: Parallel exploration of multiple solution paths
        tasks = [
            self.generate(instruction="Solve using casework and enumeration"),
            self.generate(instruction="Solve using recursive relations"),
            self.generate(instruction="Solve using symmetry or invariants"),
            self.generate(instruction="Solve using direct formula derivation")
        ]
        candidate_solutions = await asyncio.gather(*tasks)

        # Step 3: Summarize each candidate to extract core logic
        summarized_candidates = []
        for sol in candidate_solutions:
            summary = await self.summarize(context_to_summarize=sol)
            summarized_candidates.append(summary)

        # Step 4: Ensemble to converge on the best answer
        final_answer = await self.ensemble(
            instruction="Compare these four solution summaries. Identify the one that satisfies all constraints and makes logical sense. Return only the integer answer.",
            contexts_to_ensemble=summarized_candidates
        )

        # Optional: If ensemble output seems uncertain, refine further
        if "not confident" in final_answer.lower() or not final_answer.strip().isdigit():
            refined = await self.revise(
                instruction="Refine the solution by checking for edge cases and verifying consistency with the original problem constraints.",
                context_to_revise=final_answer
            )
            final_answer = refined

        return final_answer