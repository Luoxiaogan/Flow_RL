# Workflow ID: limr_117_0
# Benchmark: limr
# Data Indices: [177, 41]

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

        # Step 1: Initial Analysis - Classify and Decompose
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Identify the domain (geometry, number theory, algebra, etc.).
            2. Extract key components (variables, constraints, relationships).
            3. Highlight potential solution strategies.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Attempt solution using algebraic methods: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Attempt solution using geometric interpretation: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Attempt solution using combinatorial reasoning: {analysis}",
                context=analysis
            )
        )

        # Step 3: Refine Each Strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Refine this solution attempt: Ensure all steps are clear, logical, and accurate.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesize Best Solution
        synthesis = await self.ensemble(
            instruction="""Evaluate and synthesize the refined strategies:
            1. Check for correctness and completeness.
            2. Select the most promising approach or combine insights.
            3. Ensure the final answer is an integer between 000 and 999.""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Verification and Presentation
        final_solution = await self.revise(
            instruction="Verify the final solution: Cross-check calculations, validate logic, and format the answer as a 3-digit integer.",
            context=synthesis
        )

        return final_solution