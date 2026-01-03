# Workflow ID: limr_14_0
# Benchmark: limr
# Data Indices: [166, 58]

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
        classification = await self.generate(
            instruction="""Analyze the problem and classify it into one or more categories:
            - Algebraic: Equations, inequalities, polynomials
            - Geometric: Shapes, coordinates, transformations
            - Combinatorial: Counting, permutations, probability
            - Numerical: Approximations, computations, optimizations
            Provide a structured breakdown of the problem type and key characteristics.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop an algebraic solution strategy based on: {classification}",
                context=""
            ),
            self.generate(
                instruction=f"Develop a geometric solution strategy based on: {classification}",
                context=""
            ),
            self.generate(
                instruction=f"Develop a combinatorial solution strategy based on: {classification}",
                context=""
            ),
            self.generate(
                instruction=f"Develop a numerical solution strategy based on: {classification}",
                context=""
            )
        )

        # Step 3: Validation and Refinement
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine the following strategy: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Ensemble Synthesis
        synthesis = await self.ensemble(
            instruction="Synthesize the best solution from the following strategies, ensuring coherence and correctness.",
            contexts_list=refined_strategies
        )

        # Step 5: Final Verification
        final_verification = await self.revise(
            instruction="Perform a final verification of the solution, ensuring it satisfies all problem requirements and constraints.",
            context=synthesis
        )

        return final_verification