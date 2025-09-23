# Workflow ID: drop_223_0
# Benchmark: drop
# Data Indices: [63, 440]

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

        # Step 1: Initial Analysis (parallel extraction and classification)
        entities_task = self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage:
            - Entities: [names, roles, locations]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities]""",
            context=""
        )
        classification_task = self.generate(
            instruction="""Classify the problem type:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: Tallying instances
            - Comparison: Greater than, less than, etc.
            - Span Extraction: Exact text spans
            - Multi-step: Requires chaining operations""",
            context=""
        )
        entities, classification = await asyncio.gather(entities_task, classification_task)

        # Step 2: Entity Resolution
        resolved_entities = await self.generate(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Passage entities: {entities}
            Question: {{QUESTION}}
            Resolve all references in the question to specific entities.""",
            context=entities
        )

        # Step 3: Operation Mapping
        operation = await self.generate(
            instruction=f"""Map the question to the required operation(s):
            Problem type: {classification}
            Resolved entities: {resolved_entities}
            Identify the specific operation(s) needed to answer the question.""",
            context=resolved_entities
        )

        # Step 4: Execution
        result = await self.generate(
            instruction=f"""Execute the identified operation(s):
            Operation: {operation}
            Resolved entities: {resolved_entities}
            Perform the required calculations or reasoning steps.""",
            context=operation
        )

        # Step 5: Synthesis and Refinement
        refined_result = await self.revise(
            instruction="""Refine the result:
            - Ensure correct format (number, date, text span)
            - Address any ambiguities
            - Validate against the question requirements""",
            context=result
        )

        return refined_result