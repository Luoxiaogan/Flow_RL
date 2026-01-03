# Workflow ID: drop_131_0
# Benchmark: drop
# Data Indices: [314, 245]

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

        # Initial analysis: Extract entities and classify question type
        extraction_task = self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage:
            - Entities: Names, places, organizations, etc.
            - Numbers: Values and what they represent
            - Relationships: Connections between entities and numbers
            Format as a structured list.""",
            context=""
        )
        classification_task = self.generate(
            instruction="""Classify the question type and identify required operations:
            - Is it arithmetic, counting, comparison, or span extraction?
            - What operations are implied by the question phrasing?""",
            context=""
        )
        extraction, classification = await asyncio.gather(extraction_task, classification_task)

        # Parallel processing: Resolve references and validate operations
        reference_resolution = self.revise(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Passage context: {extraction}
            Ensure all references are mapped correctly.""",
            context=extraction
        )
        operation_validation = self.revise(
            instruction=f"""Validate the identified operations:
            Classification: {classification}
            Ensure operations align with the question requirements.""",
            context=classification
        )
        resolved_references, validated_operations = await asyncio.gather(reference_resolution, operation_validation)

        # Conditional execution based on operation type
        if "arithmetic" in validated_operations.lower():
            result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                Extracted numbers: {resolved_references}
                Operations: {validated_operations}
                Show all steps and maintain precision.""",
                context=resolved_references
            )
        elif "counting" in validated_operations.lower():
            result = await self.generate(
                instruction=f"""Count instances of entities or events:
                Extracted entities: {resolved_references}
                Operations: {validated_operations}
                Count carefully and verify.""",
                context=resolved_references
            )
        elif "comparison" in validated_operations.lower():
            result = await self.generate(
                instruction=f"""Compare values or spans:
                Extracted data: {resolved_references}
                Operations: {validated_operations}
                Clearly state which is greater/longer/etc.""",
                context=resolved_references
            )
        else:  # Span extraction
            result = await self.generate(
                instruction=f"""Extract exact text spans matching the question:
                Passage context: {resolved_references}
                Operations: {validated_operations}
                Ensure the span matches exactly as it appears.""",
                context=resolved_references
            )

        # Synthesis and validation
        final_answer = await self.ensemble(
            instruction=f"""Select the best-formatted answer:
            Candidate: {result}
            Ensure compliance with expected format (number, date, or exact span).""",
            contexts_list=[result]
        )

        return final_answer