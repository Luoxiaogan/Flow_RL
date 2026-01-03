# Workflow ID: limr_133_0
# Benchmark: limr
# Data Indices: [38, 254]

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

        # Step 1: Initial Analysis and Classification
        classification = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key components (e.g., variables, constraints, relationships).
            - Classify the problem type (e.g., geometry, number theory, algebra).
            - Highlight any special conditions or requirements.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Attempt solution using algebraic manipulation...",
                context=classification
            ),
            self.generate(
                instruction="Attempt solution using geometric visualization...",
                context=classification
            ),
            self.generate(
                instruction="Attempt solution using combinatorial reasoning...",
                context=classification
            )
        )

        # Step 3: Validation and Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="Select the most correct and complete solution. Merge insights if necessary.",
            contexts_list=refined_solutions
        )

        # Step 5: Iterative Refinement (Optional)
        while "unclear" in final_solution.lower() or "ambiguous" in final_solution.lower():
            final_solution = await self.revise(
                instruction="Address remaining ambiguities or gaps in the solution.",
                context=final_solution
            )

        return final_solution