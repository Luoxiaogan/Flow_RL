# Workflow ID: high_level_math_ganluo_21_0
# Benchmark: high_level_math_ganluo
# Data Indices: [770, 183]

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

        # Step 1: Initial Problem Analysis
        analysis = await self.generate(
            instruction="Identify the primary mathematical domain and key constraints in this problem.",
            context=""
        )

        # Step 2: Parallel Strategy Generation
        strategy_instructions = [
            "Propose a geometric interpretation or coordinate-based solution path.",
            "Suggest an algebraic manipulation or equation-based approach.",
            "Outline a combinatorial or case-analysis method if applicable.",
            "Consider number-theoretic techniques like modular arithmetic or divisibility rules."
        ]
        tasks = [self.generate(instruction=inst, context=analysis) for inst in strategy_instructions]
        strategies = await asyncio.gather(*tasks)

        # Step 3: Summarize Each Strategy
        summarized_strategies = []
        for s in strategies:
            summary = await self.summarize(context_to_summarize=s)
            summarized_strategies.append(summary)

        # Step 4: Ensemble Final Answer
        final_answer = await self.ensemble(
            instruction="Select the most consistent and mathematically sound solution from the following approaches.",
            contexts_to_ensemble=summarized_strategies
        )

        # Optional: If ensemble result seems uncertain, revise once more
        if "uncertain" in final_answer.lower() or "ambiguous" in final_answer.lower():
            final_answer = await self.revise(
                instruction="Refine the answer by resolving inconsistencies between the proposed methods.",
                context_to_revise=final_answer
            )

        return final_answer