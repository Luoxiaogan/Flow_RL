# Workflow ID: limr_105_0
# Benchmark: limr
# Data Indices: [201, 265]

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

        # Step 1: Initial Analysis - Classify problem and extract key information
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the domain (e.g., algebra, geometry, combinatorics).
            - Extract key variables, constraints, and relationships.
            - Suggest potential solution strategies.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution attempts
        attempts = await asyncio.gather(
            self.generate(
                instruction=f"Attempt 1: Solve using algebraic methods. Key info: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Attempt 2: Solve using geometric reasoning. Key info: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Attempt 3: Solve using combinatorial techniques. Key info: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Step 3: Validation - Critique and refine each attempt
        refined_attempts = await asyncio.gather(
            *[self.revise(
                instruction="Critique and improve this solution attempt.",
                context=attempt
            ) for attempt in attempts]
        )

        # Step 4: Synthesis - Select or combine the best solution
        synthesis = await self.ensemble(
            instruction="Compare all solution attempts and select the most promising one. Combine insights if necessary.",
            contexts_list=refined_attempts
        )

        # Step 5: Iterative Refinement - Refine the selected solution
        refined_solution = await self.revise(
            instruction="Refine the selected solution for clarity, precision, and correctness.",
            context=synthesis
        )

        # Step 6: Final Output - Summarize the solution
        final_output = await self.summarize(
            instruction="Condense the solution into a clear, concise format suitable for submission.",
            context=refined_solution
        )

        return final_output