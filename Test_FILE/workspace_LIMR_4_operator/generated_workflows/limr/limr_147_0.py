# Workflow ID: limr_147_0
# Benchmark: limr
# Data Indices: [287, 24]

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

        # Stage 1: Problem Analysis and Classification
        classification = await self.generate(
            instruction="""Analyze the problem and classify it:
            - Identify the main mathematical domain (geometry, number theory, etc.)
            - Extract key entities, constraints, and relationships
            - Determine the expected answer format and precision requirements
            Provide a structured breakdown.""",
            context=""
        )

        # Stage 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the classification: {classification}
                Develop a solution using algebraic techniques.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using the classification: {classification}
                Develop a solution using geometric techniques.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using the classification: {classification}
                Develop a solution using combinatorial techniques.""",
                context=classification
            )
        )

        # Stage 3: Iterative Refinement and Validation
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Improve clarity, add missing details, and validate correctness.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Stage 4: Ensemble Synthesis and Final Answer Extraction
        final_solution = await self.ensemble(
            instruction="Synthesize the best solution from all refined strategies and extract the final answer.",
            contexts_list=refined_strategies
        )

        # Stage 5: Edge Case Handling and Robustness Checks
        validation = await self.generate(
            instruction=f"""Validate the final solution:
            - Check for edge cases
            - Verify all constraints are satisfied
            - Ensure the answer format and precision meet requirements""",
            context=final_solution
        )

        # Return the final validated solution
        return validation