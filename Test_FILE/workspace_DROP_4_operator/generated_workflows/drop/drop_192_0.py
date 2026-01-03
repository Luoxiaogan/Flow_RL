# Workflow ID: drop_192_0
# Benchmark: drop
# Data Indices: [143, 357]

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

        # Step 1: Extract entities, numbers, and relationships
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, places, organizations
            - Numbers: Values and what they represent
            - Relationships: Connections between entities and numbers
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references and clarify ambiguities
        resolved = await self.revise(
            instruction="""Resolve pronouns and partial names to specific entities:
            - Ensure all references are clear and unambiguous
            - Maintain consistency with the passage""",
            context=extraction
        )

        # Step 3: Classify the question type and identify operations
        classification = await self.generate(
            instruction="""Analyze the question and classify its type:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: Tally occurrences
            - Comparison: Greater than, less than
            - Span Extraction: Exact text spans
            Specify the required operations and their order.""",
            context=resolved
        )

        # Step 4: Execute operations in parallel
        operations = classification.split("\n")
        results = await asyncio.gather(
            *[self.generate(
                instruction=f"Perform the following operation: {op}",
                context=resolved
            ) for op in operations if op.strip()]
        )

        # Step 5: Synthesize results and format the answer
        synthesis = await self.ensemble(
            instruction="""Combine the results into a coherent answer:
            - Ensure all operations are accounted for
            - Format the answer according to the question requirements""",
            contexts_list=results
        )

        final_answer = await self.summarize(
            instruction="Condense the synthesized result into the final answer format.",
            context=synthesis
        )

        return final_answer