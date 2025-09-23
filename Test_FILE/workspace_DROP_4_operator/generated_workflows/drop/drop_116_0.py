# Workflow ID: drop_116_0
# Benchmark: drop
# Data Indices: [239, 475]

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

        # Phase 1: Initial Analysis - Extract entities, numbers, and relationships
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Phase 2: Reference Resolution - Resolve pronouns and partial names
        reference_resolution = await self.revise(
            instruction=f"""Resolve all pronouns and partial names in the passage to specific entities.
            Use the extracted entities and context to disambiguate references.
            Entities: {entities_extraction}""",
            context=entities_extraction
        )

        # Phase 3: Operation Identification - Determine the required operation(s)
        operation_identification = await self.generate(
            instruction=f"""Analyze the question to determine the required operation(s).
            Classify the question type (e.g., arithmetic, counting, comparison) and identify the relevant entities and numbers.
            Resolved references: {reference_resolution}""",
            context=reference_resolution
        )

        # Phase 4: Operation Execution - Perform the identified operations
        operation_execution = await self.generate(
            instruction=f"""Perform the identified operations using the resolved entities and numbers.
            Show all steps and validate intermediate results.
            Operations: {operation_identification}""",
            context=operation_identification
        )

        # Phase 5: Validation and Answer Extraction - Validate results and extract the final answer
        validation_and_extraction = await self.revise(
            instruction=f"""Validate the results against the passage and extract the final answer in the required format (number, date, or text span).
            Ensure the answer matches the passage exactly.
            Results: {operation_execution}""",
            context=operation_execution
        )

        # Phase 6: Ensemble - Combine multiple perspectives if needed
        final_answer = await self.ensemble(
            instruction="Synthesize all perspectives into the most accurate and complete answer.",
            contexts_list=[validation_and_extraction, operation_execution, reference_resolution]
        )

        return final_answer