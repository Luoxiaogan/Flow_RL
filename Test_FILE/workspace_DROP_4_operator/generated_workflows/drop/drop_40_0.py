# Workflow ID: drop_40_0
# Benchmark: drop
# Data Indices: [289, 363]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple interpretations
        interpretations = await asyncio.gather(
            self.generate(
                instruction=f"""Interpret the problem as an arithmetic task:
                - Identify numbers and their relationships
                - Determine required operations (addition, subtraction, etc.)
                - Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Interpret the problem as a span extraction task:
                - Identify relevant text spans
                - Resolve references (e.g., pronouns, partial names)
                - Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Interpret the problem as a comparison task:
                - Identify entities to compare
                - Determine the basis of comparison
                - Context: {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Check consistency and refine
        refined_interpretations = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine this interpretation. Correct any errors in entity mapping or operation identification.",
                context=interp
            ) for interp in interpretations]
        )

        # Step 4: Execution - Perform identified operations
        execution_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Execute the identified operations in this interpretation:
                - Perform arithmetic calculations if applicable
                - Extract exact text spans if applicable
                - Compare entities if applicable
                - Context: {interp}""",
                context=interp
            ) for interp in refined_interpretations]
        )

        # Step 5: Final Evaluation - Ensemble decision-making
        final_answer = await self.ensemble(
            instruction="Evaluate these solutions and select the most plausible answer. Ensure it matches the expected format (number, date, or exact text span).",
            contexts_list=execution_results
        )

        return final_answer