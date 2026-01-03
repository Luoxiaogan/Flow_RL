# Workflow ID: limr_90_0
# Benchmark: limr
# Data Indices: [14, 230]

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

        # Step 1: Initial Analysis - Understand the problem structure
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify key components (variables, equations, constraints).
            - Classify the problem type (geometry, number theory, etc.).
            - Highlight any special cases or edge conditions.
            - Suggest potential solution strategies.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Develop an algebraic solution approach.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Develop a geometric interpretation if applicable.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Explore combinatorial or probabilistic methods.",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Critique and improve each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Critique and refine this approach:\n{strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesis - Combine insights from all strategies
        synthesis = await self.ensemble(
            instruction="""Synthesize the refined strategies into a unified solution:
            - Select the most promising approach.
            - Combine complementary insights from different strategies.
            - Ensure logical consistency and mathematical rigor.""",
            contexts_list=refined_strategies
        )

        # Step 5: Iterative Improvement - Validate and refine the final solution
        final_solution = synthesis
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the solution for correctness and completeness.",
                context=final_solution
            )
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Address issues identified in validation:\n{validation}",
                    context=final_solution
                )
            else:
                break

        # Step 6: Final Answer Extraction - Ensure the answer meets the required format
        final_answer = await self.generate(
            instruction="""Extract the final answer:
            - Ensure it is an integer between 000 and 999.
            - Verify precision and correctness.
            - Format the answer clearly.""",
            context=final_solution
        )

        return final_answer