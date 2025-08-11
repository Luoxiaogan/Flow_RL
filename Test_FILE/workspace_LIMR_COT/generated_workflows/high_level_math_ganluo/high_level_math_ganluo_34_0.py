# Workflow ID: high_level_math_ganluo_34_0
# Benchmark: high_level_math_ganluo
# Data Indices: [986, 777]

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
        task1 = self.generate("Generate an algebraic approach to solve this problem.")
        task2 = self.generate("Generate a geometric approach to solve this problem.")
        task3 = self.generate("Generate a combinatorial or number-theoretic approach if applicable.")
        task4 = self.generate("Generate a recursive or symmetry-based approach.")

        strategies = await asyncio.gather(task1, task2, task3, task4)

        # Step 2: Extract key facts from each strategy for structured reasoning
        extracted_facts = []
        for i, strategy in enumerate(strategies):
            fact = await self.generate(
                f"From this strategy, extract the core mathematical elements: variables, equations, constraints.",
                context=strategy
            )
            extracted_facts.append(fact)

        # Step 3: Refine each candidate solution through iterative revision
        refined_solutions = []
        for i, fact in enumerate(extracted_facts):
            solution = await self.generate(
                f"Using these facts, construct a complete solution to the problem.",
                context=fact
            )
            # Revise once per solution to catch errors
            revised_solution = await self.revise(
                "Check for internal consistency, logical gaps, and correctness of math steps.",
                context_to_revise=solution
            )
            refined_solutions.append(revised_solution)

        # Step 4: Ensemble the best solution
        final_answer = await self.ensemble(
            "Select the most consistent, clear, and mathematically sound solution among the candidates.",
            contexts_to_ensemble=refined_solutions
        )

        return final_answer