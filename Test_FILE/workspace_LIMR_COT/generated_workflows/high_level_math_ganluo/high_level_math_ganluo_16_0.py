# Workflow ID: high_level_math_ganluo_16_0
# Benchmark: high_level_math_ganluo
# Data Indices: [981, 538]

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
        analysis = await self.generate(
            instruction="Identify the mathematical domain (e.g., geometry, number theory) and key constraints of this problem."
        )

        # Step 2: Explore multiple solution strategies in parallel
        tasks = [
            self.generate(instruction="Solve using algebraic methods."),
            self.generate(instruction="Approach using geometric reasoning or coordinate bashing."),
            self.generate(instruction="Apply combinatorial casework or recursive reasoning."),
            self.generate(instruction="Use modular arithmetic or number-theoretic properties.")
        ]
        candidates = await asyncio.gather(*tasks)

        # Step 3: Refine each candidate solution
        revised_candidates = []
        for candidate in candidates:
            rev1 = await self.revise(instruction="Check for logical consistency and internal coherence.", context_to_revise=candidate)
            rev2 = await self.revise(instruction="Verify edge cases or boundary conditions.", context_to_revise=rev1)
            revised_candidates.append(rev2)

        # Step 4: Ensemble to find the best-supported solution
        final_answer = await self.ensemble(
            instruction="Select the most consistent and mathematically sound solution from the candidates.",
            contexts_to_ensemble=revised_candidates
        )

        return final_answer