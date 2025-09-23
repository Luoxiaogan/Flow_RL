# Workflow ID: limr_20_0
# Benchmark: limr
# Data Indices: [130, 25]

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

        # Initial Analysis Phase
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Classify the problem type (e.g., algebra, geometry, number theory).
            2. Extract key entities, numbers, and relationships.
            3. Identify explicit and implicit constraints.
            Provide structured output.""",
            context=""
        )

        # Hierarchical Decomposition
        decomposition = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Break the problem into sub-problems:
            - Define each sub-problem clearly.
            - Specify dependencies between sub-problems.
            - Highlight any edge cases.""",
            context=initial_analysis
        )

        # Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using geometric methods:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using combinatorial methods:
                {decomposition}""",
                context=decomposition
            )
        )

        # Validation and Refinement Loop
        refined_strategies = []
        for strategy in strategies:
            validated = await self.revise(
                instruction="Validate this solution for correctness and completeness.",
                context=strategy
            )
            refined_strategies.append(validated)

        # Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Evaluate each approach for correctness, elegance, and efficiency.
            - Combine insights from complementary strategies.
            - Ensure the final answer is an integer between 000 and 999.""",
            contexts_list=refined_strategies
        )

        # Final Verification
        verified_solution = await self.revise(
            instruction="Perform final verification: check logical consistency, constraints, and format.",
            context=final_solution
        )

        return verified_solution