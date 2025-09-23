# Workflow ID: limr_95_0
# Benchmark: limr
# Data Indices: [90, 176]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Classify the problem type (algebra, geometry, combinatorics, etc.)
            - Identify key entities, numbers, and relationships
            - List all constraints and conditions
            - Suggest potential solution strategies""",
            context=""
        )

        # Step 2: Parallel Exploration
        strategies = ["algebraic", "combinatorial", "geometric", "numerical"]
        parallel_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Attempt to solve the problem using {strategy} methods:
                - Show all steps clearly
                - Maintain precision
                - Validate intermediate results""",
                context=initial_analysis
            ) for strategy in strategies]
        )

        # Step 3: Intermediate Validation
        validated_attempts = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate this solution attempt:
                - Check for logical consistency
                - Verify calculations
                - Ensure all constraints are satisfied
                - Suggest improvements if necessary""",
                context=attempt
            ) for attempt in parallel_attempts]
        )

        # Step 4: Synthesis and Selection
        final_solution = await self.ensemble(
            instruction="""Compare all solution attempts and select the best one:
            - Evaluate completeness and correctness
            - Prefer exact solutions over approximations
            - Synthesize insights from all attempts""",
            contexts_list=validated_attempts
        )

        # Step 5: Final Refinement
        polished_solution = await self.revise(
            instruction="""Refine the final solution:
            - Ensure clarity and precision
            - Present the answer in the required format (integer between 000 and 999)
            - Double-check all steps""",
            context=final_solution
        )

        return polished_solution