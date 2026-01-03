# Workflow ID: drop_218_0
# Benchmark: drop
# Data Indices: [201, 140]

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
            - Entities: Names, places, organizations, etc.
            - Numbers: Quantities, dates, measurements, etc.
            - Relationships: Actions, events, and connections between entities
            - Reference Mappings: Map pronouns and partial names to specific entities
            Format as a structured list.""",
            context=""
        )

        # Step 2: Analyze the question and identify required operation(s)
        analysis = await self.generate(
            instruction=f"""Analyze the question and classify its type:
            - Is it numerical, logical, or textual?
            - Does it involve counting, arithmetic, comparison, or span extraction?
            - What is the expected answer format?
            Passage Context: {extraction}""",
            context=""
        )

        refined_analysis = await self.revise(
            instruction="Validate and refine the classification and operation proposal.",
            context=analysis
        )

        # Step 3: Execute the identified operation(s) in parallel
        operations = ["addition", "subtraction", "counting", "comparison", "span_extraction"]
        results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Perform the following operation: {op}
                Passage Context: {extraction}
                Question Analysis: {refined_analysis}""",
                context=""
            ) for op in operations]
        )

        # Step 4: Select the best result using ensemble
        best_result = await self.ensemble(
            instruction="""Select the most plausible result based on:
            - Consistency with the passage
            - Alignment with the question
            - Correctness of the operation""",
            contexts_list=results
        )

        # Step 5: Format the answer to match expected output
        formatted_answer = await self.revise(
            instruction=f"""Format the answer to match the expected output:
            - Ensure it's a number, date, or exact text span
            - Cross-check with the question and passage
            Best Result: {best_result}""",
            context=extraction
        )

        return formatted_answer