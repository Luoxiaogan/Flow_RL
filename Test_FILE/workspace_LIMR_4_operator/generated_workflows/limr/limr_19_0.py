# Workflow ID: limr_19_0
# Benchmark: limr
# Data Indices: [95, 121]

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
        
        # Step 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem in detail:
            1. Identify the primary domain (geometry, algebra, etc.).
            2. Extract all given data, constraints, and relationships.
            3. Classify the problem type (numerical, symbolic, proof-based, etc.).
            4. Suggest potential solution strategies.
            Provide structured output.""",
            context=""
        )
        
        # Step 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Explore algebraic methods: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Explore geometric methods: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Explore combinatorial methods: {analysis}",
                context=analysis
            )
        )
        
        # Step 3: Intermediate Validation and Refinement
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine this approach. Correct errors and fill gaps.",
                context=strategy
            ) for strategy in strategies]
        )
        
        # Step 4: Synthesis and Decision-Making
        synthesis = await self.ensemble(
            instruction="""Synthesize the refined strategies:
            1. Evaluate each approach for rigor and completeness.
            2. Select the best solution or combine insights.
            3. Ensure the final answer meets the problem's requirements.""",
            contexts_list=refined_strategies
        )
        
        # Step 5: Final Verification and Output
        final_solution = await self.revise(
            instruction="Verify the final solution. Ensure it is precise, complete, and formatted correctly.",
            context=synthesis
        )
        
        return final_solution