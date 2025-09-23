# Workflow ID: limr_96_0
# Benchmark: limr
# Data Indices: [290, 141]

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

        # Phase 1: Initial Analysis and Decomposition
        analysis = await self.generate(
            instruction="""Analyze the problem and break it into key components:
            - Identify the problem type (e.g., number theory, combinatorics)
            - Extract all numbers, variables, and relationships
            - Outline potential solution strategies
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Solve using algebraic manipulation and equations.",
                context=analysis
            ),
            self.generate(
                instruction="Solve using combinatorial reasoning and counting principles.",
                context=analysis
            ),
            self.generate(
                instruction="Solve using geometric or spatial reasoning.",
                context=analysis
            )
        )

        # Phase 3: Validation and Refinement
        validated_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Phase 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the validated strategies:
            - Select the most elegant or efficient approach
            - Combine insights from multiple strategies if needed
            - Ensure the solution meets all problem constraints""",
            contexts_list=validated_strategies
        )

        # Phase 5: Final Output and Formatting
        formatted_solution = await self.generate(
            instruction=f"""Format the final solution as an integer between 000 and 999:
            Final solution: {final_solution}""",
            context=""
        )

        return formatted_solution