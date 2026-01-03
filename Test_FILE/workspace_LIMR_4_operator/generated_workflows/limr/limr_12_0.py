# Workflow ID: limr_12_0
# Benchmark: limr
# Data Indices: [284, 8]

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

        # Step 1: Initial Analysis and Problem Decomposition
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify known variables and constants
            - Extract constraints and relationships
            - Classify the problem type (e.g., geometry, number theory)
            - Propose potential solution strategies""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = ["algebraic", "geometric", "combinatorial", "numerical"]
        parallel_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve the problem using {strategy} approach",
                context=initial_analysis
            ) for strategy in strategies]
        )

        # Step 3: Validation and Refinement
        refined_solutions = []
        for attempt in parallel_attempts:
            validation = await self.generate(
                instruction="Validate this solution for correctness, completeness, and adherence to constraints",
                context=attempt
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix issues identified in validation: {validation}",
                    context=attempt
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(attempt)

        # Step 4: Summarization for Ensemble
        summarized_solutions = await asyncio.gather(
            *[self.summarize(
                instruction="Condense this solution while preserving key insights",
                context=solution
            ) for solution in refined_solutions]
        )

        # Step 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Mathematical rigor
            - Alignment with problem constraints
            - Simplicity and elegance
            - Computational efficiency""",
            contexts_list=summarized_solutions
        )

        return final_solution