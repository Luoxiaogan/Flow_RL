# Workflow ID: limr_53_0
# Benchmark: limr
# Data Indices: [35, 243]

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
            instruction="""Analyze the problem thoroughly:
            - Classify the problem type (e.g., algebraic, geometric, combinatorial).
            - Identify key components, variables, and constraints.
            - Highlight any special conditions or requirements.
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop an algebraic solution strategy based on: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Develop a geometric solution strategy based on: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Develop a combinatorial solution strategy based on: {analysis}",
                context=analysis
            )
        )

        # Phase 3: Validation and Refinement
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction=f"Validate and refine this strategy: {strategy}. Check for errors, logical gaps, and missing details.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Phase 4: Iterative Refinement
        final_strategies = []
        for refined in refined_strategies:
            summary = await self.summarize(
                instruction=f"Condense this strategy into key insights: {refined}",
                context=refined
            )
            final_strategies.append(summary)

        # Phase 5: Synthesis and Finalization
        final_answer = await self.ensemble(
            instruction="Select the best solution path and synthesize it into a final answer. Ensure the answer is an integer between 000 and 999.",
            contexts_list=final_strategies
        )

        return final_answer