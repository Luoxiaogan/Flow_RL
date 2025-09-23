# Workflow ID: limr_128_0
# Benchmark: limr
# Data Indices: [269, 281]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify its type (geometry, number theory, etc.)
            - Extract key entities, numbers, and relationships
            - List all constraints and conditions
            - Highlight any special cases or edge conditions
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Strategy Generation
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Develop a solution using algebraic methods:
                - Show all transformations and calculations
                - Maintain full precision
                - Highlight assumptions""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Develop a solution using geometric methods:
                - Use coordinate geometry or vector analysis
                - Include diagrams or visual reasoning if applicable
                - Verify consistency with constraints""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {analysis}
                Develop a solution using combinatorial methods:
                - Apply counting principles or probability
                - Consider permutations, combinations, or recursive sequences
                - Ensure logical consistency""",
                context=analysis
            )
        )

        # Step 3: Intermediate Verification
        verified_strategies = []
        for strategy in strategies:
            revised_strategy = await self.revise(
                instruction=f"""Verify and refine this solution:
                - Check for logical consistency and computational accuracy
                - Address any gaps or ambiguities
                - Ensure compliance with problem constraints""",
                context=strategy
            )
            verified_strategies.append(revised_strategy)

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Evaluate all solutions:
            - Compare strengths and weaknesses
            - Combine complementary insights if possible
            - Select the most robust and precise solution
            Present the final answer as an integer between 000 and 999.""",
            contexts_list=verified_strategies
        )

        # Step 5: Final Refinement
        polished_solution = await self.revise(
            instruction="""Refine the final solution:
            - Ensure clarity and precision
            - Double-check all calculations
            - Format the answer as a three-digit integer""",
            context=final_solution
        )

        return polished_solution