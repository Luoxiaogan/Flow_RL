# Workflow ID: limr_134_0
# Benchmark: limr
# Data Indices: [31, 47]

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

        # Step 1: Problem Classification and Feature Extraction
        classification = await self.generate(
            instruction="""Classify the problem into one or more categories:
            - Geometry, Number Theory, Combinatorics, Algebra, Optimization, Sequence/Series
            Extract key features such as variables, constraints, and relationships.
            Identify any special cases or edge conditions.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies in Parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using a geometric approach:
                - Use coordinate geometry, trigonometry, or vector analysis if applicable.
                - Show all steps clearly.
                Classification: {classification}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve using a number theory approach:
                - Apply modular arithmetic, divisibility rules, or prime factorization if applicable.
                - Show all steps clearly.
                Classification: {classification}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve using a combinatorics approach:
                - Use counting principles, permutations, or recursive relations if applicable.
                - Show all steps clearly.
                Classification: {classification}""",
                context=classification
            ),
            self.generate(
                instruction=f"""Solve using an algebraic approach:
                - Solve equations, manipulate polynomials, or work with complex numbers if applicable.
                - Show all steps clearly.
                Classification: {classification}""",
                context=classification
            )
        )

        # Step 3: Verify and Refine Each Strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Verify correctness and improve clarity of this solution.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesize Best Solution Using Ensemble
        final_solution = await self.ensemble(
            instruction="""Select the most rigorous, accurate, and elegant solution:
            - Consider completeness, correctness, and clarity.
            - Resolve any conflicts between solutions.""",
            contexts_list=refined_strategies
        )

        # Step 5: Summarize Key Insights and Present Final Answer
        summary = await self.summarize(
            instruction="Condense the solution into a concise, clear format with the final answer highlighted.",
            context=final_solution
        )

        return summary