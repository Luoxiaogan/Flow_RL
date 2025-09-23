# Workflow ID: drop_66_0
# Benchmark: drop
# Data Indices: [278, 416]

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

        # Step 1: Extract all relevant entities, numbers, and relationships
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, places, organizations, etc.
            - Numbers: All numerical values and what they represent
            - Relationships: Connections between entities and numbers
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references (pronouns, partial names)
        reference_resolution = await self.generate(
            instruction=f"""Resolve all references in the passage:
            - Map pronouns ('they', 'it') to specific entities
            - Clarify partial names or ambiguous terms
            Use the following extracted information:
            {entities_extraction}
            Provide a mapping of references to their resolved entities.""",
            context=entities_extraction
        )

        # Step 3: Classify the question type and identify required operations
        question_classification = await self.generate(
            instruction=f"""Classify the question type and identify required operations:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times something occurs
            - Comparison: Greater than, less than, etc.
            - Span Extraction: Exact text spans
            - Multi-step: Multiple operations or facts
            Use the following resolved references:
            {reference_resolution}
            Provide a clear classification and operation plan.""",
            context=reference_resolution
        )

        # Step 4: Execute operations based on classification
        if "arithmetic" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                - Show all steps
                - Double-check calculations
                Use the following classification:
                {question_classification}
                Provide the final result.""",
                context=question_classification
            )
        elif "counting" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Count occurrences:
                - Identify all relevant instances
                - Verify completeness
                Use the following classification:
                {question_classification}
                Provide the final count.""",
                context=question_classification
            )
        elif "comparison" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Compare values:
                - Determine which is greater, smaller, earlier, later
                Use the following classification:
                {question_classification}
                Provide the comparison result.""",
                context=question_classification
            )
        elif "span" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Extract exact text spans:
                - Match question requirements
                Use the following classification:
                {question_classification}
                Provide the exact span.""",
                context=question_classification
            )
        else:
            # Default to multi-step reasoning
            result = await self.generate(
                instruction=f"""Solve using multi-step reasoning:
                - Combine multiple operations or facts
                Use the following classification:
                {question_classification}
                Provide the final answer.""",
                context=question_classification
            )

        # Step 5: Format the answer appropriately
        formatted_answer = await self.revise(
            instruction=f"""Format the answer:
            - Ensure it matches expected format (number, date, text span)
            - Validate correctness
            Use the following result:
            {result}
            Provide the final formatted answer.""",
            context=result
        )

        return formatted_answer