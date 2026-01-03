# Workflow ID: drop_208_0
# Benchmark: drop
# Data Indices: [399, 447]

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

        # Step 1: Initial Analysis - Extract Entities and Numbers
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: People, places, organizations
            - Numbers: Values and what they represent
            - Relationships: Actions, events, and their connections
            Format as structured list.""",
            context=""
        )

        # Step 2: Parallel Fork - Entity Resolution and Operation Identification
        entity_resolution, operation_identification = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve all references in the question to specific entities:
                - Map pronouns and partial names to full names
                - Ensure all references are unambiguous
                Entities extracted: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Identify the required operation based on the question:
                - Arithmetic: Addition, subtraction, etc.
                - Counting: How many times, how many different
                - Comparison: Greater, lesser, earlier, later
                - Span Extraction: Exact text spans
                Question: {self.problem_text.split('QUESTION:')[1].split('ANSWER:')[0].strip()}
                Entities extracted: {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Step 3: Merge and Execute - Combine Results and Perform Operation
        operation_result = await self.ensemble(
            instruction="""Combine entity resolution and operation identification:
            - Use resolved entities to perform the identified operation
            - Handle ambiguities by prioritizing contextually relevant entities
            - Execute the operation carefully, ensuring accuracy
            Provide the result of the operation.""",
            contexts_list=[entity_resolution, operation_identification]
        )

        # Step 4: Validation and Refinement - Ensure Correct Format
        refined_result = await self.revise(
            instruction="""Validate the result:
            - Ensure it matches the expected format (number, date, text span)
            - Correct any errors or inconsistencies
            - Add missing details if necessary
            Original result: {operation_result}""",
            context=operation_result
        )

        # Step 5: Output - Return Final Answer
        return refined_result