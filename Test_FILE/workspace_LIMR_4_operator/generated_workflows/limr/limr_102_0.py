# Workflow ID: limr_102_0
# Benchmark: limr
# Data Indices: [259, 183]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Decompose the problem
        decomposition = await self.generate(
            instruction="""Analyze the problem and extract key components:
            - Variables and constants
            - Relationships and constraints
            - Known and unknown quantities
            - Problem type (geometry, algebra, combinatorics, etc.)
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Explore multiple solution strategies in parallel
        strategies = [
            "Geometric approach using coordinate geometry and trigonometry.",
            "Algebraic approach involving equations and inequalities.",
            "Combinatorial approach using counting principles and probability.",
            "Number-theoretic approach focusing on modular arithmetic and divisibility."
        ]
        explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve the problem using {strategy}:\n{decomposition}",
                context=decomposition
            ) for strategy in strategies]
        )

        # Step 3: Iteratively refine intermediate results
        refined_results = []
        for exploration in explorations:
            refined = await self.revise(
                instruction="Improve clarity, correctness, and completeness. Validate all steps.",
                context=exploration
            )
            refined_results.append(refined)

        # Step 4: Synthesize findings into a coherent solution
        synthesis = await self.ensemble(
            instruction="Evaluate all approaches and synthesize into a unified solution. Select the most rigorous and complete option.",
            contexts_list=refined_results
        )

        # Step 5: Handle edge cases and uncertainty
        if "undefined" in synthesis.lower() or "error" in synthesis.lower():
            fallback = await self.generate(
                instruction="Address edge cases or ambiguities. Explore alternative approaches.",
                context=synthesis
            )
            return fallback

        return synthesis