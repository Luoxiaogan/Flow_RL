# Workflow ID: limr_123_0
# Benchmark: limr
# Data Indices: [145, 29]

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

        # Step 1: Initial Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem deeply:
            - Identify the problem type (geometry, number theory, etc.)
            - Extract all numerical entities, constraints, and relationships
            - Determine the expected answer format (integer between 000 and 999)
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="""Solve using algebraic methods:
                - Use symbolic manipulation and transformations
                - Maintain full precision in calculations
                - Present intermediate steps clearly""",
                context=analysis
            ),
            self.generate(
                instruction="""Solve using geometric reasoning:
                - Analyze spatial relationships or use coordinate geometry
                - Visualize the problem if applicable
                - Derive conclusions from geometric properties""",
                context=analysis
            ),
            self.generate(
                instruction="""Solve using combinatorial techniques:
                - Count possibilities or apply probability principles
                - Use permutations, combinations, or recursive sequences
                - Ensure logical consistency in counting arguments""",
                context=analysis
            )
        )

        # Step 3: Intermediate Validation and Refinement
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Critique and improve this solution:\n{strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Compare the refined strategies for correctness and completeness
            - Select the most robust solution or combine insights from multiple approaches
            - Ensure the final answer is an integer between 000 and 999""",
            contexts_list=refined_strategies
        )

        # Step 5: Iterative Refinement (if needed)
        validation = await self.generate(
            instruction="Validate the final solution for correctness and completeness.",
            context=final_solution
        )
        if "error" in validation.lower() or "incomplete" in validation.lower():
            final_solution = await self.revise(
                instruction=f"Address issues in the solution: {validation}",
                context=final_solution
            )

        return final_solution