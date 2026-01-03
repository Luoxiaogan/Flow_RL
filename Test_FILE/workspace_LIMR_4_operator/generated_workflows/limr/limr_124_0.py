# Workflow ID: limr_124_0
# Benchmark: limr
# Data Indices: [190, 188]

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

        # Phase 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the problem type (e.g., algebraic, geometric).
            - Extract key variables, constraints, and relationships.
            - Classify the expected solution format (e.g., integer, proof).
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Parallel Exploration
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                - Perform symbolic manipulation.
                - Solve equations step-by-step.
                Initial analysis: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using combinatorial methods:
                - Apply counting principles.
                - Use probabilistic reasoning if applicable.
                Initial analysis: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using geometric methods:
                - Use coordinate geometry or trigonometric identities.
                - Visualize the problem if helpful.
                Initial analysis: {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Phase 3: Validation and Refinement
        refined_approaches = await asyncio.gather(
            *[self.revise(
                instruction="""Validate and refine the solution:
                - Check for logical consistency.
                - Add missing details or correct errors.
                - Ensure all steps are clear and rigorous.""",
                context=approach
            ) for approach in approaches]
        )

        # Phase 4: Synthesis and Finalization
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Evaluate the strengths and weaknesses of each approach.
            - Select the most promising solution or combine insights.
            - Present the final answer in the required format.""",
            contexts_list=refined_approaches
        )

        return final_solution