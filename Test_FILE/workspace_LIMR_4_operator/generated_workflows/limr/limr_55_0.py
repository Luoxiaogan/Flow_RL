# Workflow ID: limr_55_0
# Benchmark: limr
# Data Indices: [214, 225]

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

        # Step 1: Problem Classification
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Geometry (e.g., 3D geometry, coordinate geometry)
            - Number Theory (e.g., modular arithmetic, Diophantine equations)
            - Combinatorics (e.g., counting principles, probability)
            - Algebra (e.g., polynomial equations, complex numbers)
            - Optimization (e.g., inequalities, extremal problems)
            Provide a structured classification with reasoning.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction="Attempt a geometric solution using coordinate geometry, vectors, or trigonometry.",
                context=classification
            ),
            self.generate(
                instruction="Attempt a number-theoretic solution using modular arithmetic, divisibility, or prime factorization.",
                context=classification
            ),
            self.generate(
                instruction="Attempt a combinatorial solution using counting principles, permutations, or probability.",
                context=classification
            ),
            self.generate(
                instruction="Attempt an algebraic solution using polynomial equations, complex numbers, or functional equations.",
                context=classification
            ),
            self.generate(
                instruction="Attempt an optimization solution using inequalities, calculus, or extremal principles.",
                context=classification
            )
        )

        # Step 3: Validation and Refinement
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this strategy: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Ensemble Selection
        final_solution = await self.ensemble(
            instruction="""Select the most promising solution based on:
            - Logical consistency
            - Precision and accuracy
            - Completeness of reasoning
            - Alignment with problem requirements""",
            contexts_list=refined_strategies
        )

        # Step 5: Summarize Final Answer
        answer = await self.summarize(
            instruction="Extract the final answer as an integer between 000 and 999.",
            context=final_solution
        )

        return answer