# Workflow ID: limr_0_0
# Benchmark: limr
# Data Indices: [99, 293]

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
            instruction="""Analyze the problem:
            - Classify the problem type (geometry, number theory, algebra, etc.)
            - Identify key components and constraints
            - Outline potential solution strategies
            Provide structured output with clear headings.""",
            context=""
        )

        # Step 2: Parallel Exploration of Approaches
        algebraic_attempt = self.generate(
            instruction=f"""Solve using algebraic methods:
            - Perform algebraic manipulations
            - Solve equations step-by-step
            - Verify intermediate results
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )
        combinatorial_attempt = self.generate(
            instruction=f"""Solve using combinatorial methods:
            - Apply counting principles
            - Explore permutations and combinations
            - Verify logical consistency
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )
        geometric_attempt = self.generate(
            instruction=f"""Solve using geometric reasoning:
            - Identify geometric properties
            - Apply relevant theorems
            - Perform calculations
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )

        attempts = await asyncio.gather(algebraic_attempt, combinatorial_attempt, geometric_attempt)

        # Step 3: Intermediate Validation
        refined_attempts = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine and validate this solution attempt: {attempt}",
                context=attempt
            ) for attempt in attempts]
        )

        # Step 4: Synthesis
        synthesis = await self.ensemble(
            instruction="Compare and synthesize the best solution from the refined attempts.",
            contexts_list=refined_attempts
        )

        # Step 5: Iterative Refinement
        for _ in range(2):  # Allow up to 2 refinement iterations
            validation = await self.generate(
                instruction=f"Validate the synthesized solution: {synthesis}. Identify any gaps or errors.",
                context=synthesis
            )
            if "error" in validation.lower() or "gap" in validation.lower():
                synthesis = await self.revise(
                    instruction=f"Refine the solution based on validation feedback: {validation}",
                    context=synthesis
                )
            else:
                break

        return synthesis