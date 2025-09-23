# Workflow ID: drop_15_0
# Benchmark: drop
# Data Indices: [110, 24]

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

        # Phase 1: Extraction
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - Entities: [names, roles, descriptions]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities]""",
            context=""
        )
        refined_extraction = await self.revise(
            instruction="Refine the extraction to ensure completeness and resolve ambiguities.",
            context=extraction
        )

        # Phase 2: Resolution
        reference_mapping = await self.generate(
            instruction=f"""Map question references to specific entities in the passage:
            Passage Entities: {refined_extraction}
            Question: {{QUESTION}}
            Resolve pronouns and partial names to specific entities.""",
            context=refined_extraction
        )
        resolved_references = await self.ensemble(
            instruction="Select the most plausible interpretation for ambiguous references.",
            contexts_list=[reference_mapping]
        )

        # Phase 3: Operation Identification
        operation_type = await self.generate(
            instruction=f"""Classify the question into one of the following operation types:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span Extraction
            Passage: {{PASSAGE}}
            Question: {{QUESTION}}""",
            context=resolved_references
        )

        # Phase 4: Execution
        if "arithmetic" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Extracted Data: {refined_extraction}
                Resolved References: {resolved_references}
                Operation: {{OPERATION}}""",
                context=operation_type
            )
        elif "counting" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Count the relevant instances:
                Extracted Data: {refined_extraction}
                Resolved References: {resolved_references}""",
                context=operation_type
            )
        elif "comparison" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Compare the specified entities/values:
                Extracted Data: {refined_extraction}
                Resolved References: {resolved_references}""",
                context=operation_type
            )
        else:  # Span extraction
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage: {{PASSAGE}}
                Question: {{QUESTION}}""",
                context=resolved_references
            )

        # Phase 5: Validation and Finalization
        validated_result = await self.revise(
            instruction="Ensure the result matches the expected format and constraints.",
            context=result
        )
        final_answer = await self.summarize(
            instruction="Condense the final result into the required format.",
            context=validated_result
        )

        return final_answer