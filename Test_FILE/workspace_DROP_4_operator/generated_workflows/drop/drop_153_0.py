# Workflow ID: drop_153_0
# Benchmark: drop
# Data Indices: [7, 173]

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

        # Step 1: Extract entities and numbers
        entities_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: People, teams, locations
            - Numbers: Scores, times, statistics
            - Relationships: Who did what, when, and how
            Format as structured JSON.""",
            context=""
        )

        # Step 2: Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            - Passage context: {entities_numbers}
            - Question references: [they, the team, etc.]
            Provide a mapping of references to entities.""",
            context=entities_numbers
        )

        # Step 3: Identify required operation(s)
        operation_identification = await self.generate(
            instruction=f"""Classify the question type and identify required operation(s):
            - Passage context: {entities_numbers}
            - Resolved references: {resolved_references}
            - Question: [QUESTION TEXT]
            Output operation type (arithmetic, counting, comparison, span extraction) and details.""",
            context=resolved_references
        )

        # Step 4: Execute operations (parallelize if multiple)
        if "arithmetic" in operation_identification.lower():
            arithmetic_result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                - Numbers: {entities_numbers}
                - Operation: [addition, subtraction, etc.]
                Show all steps and final result.""",
                context=operation_identification
            )
            intermediate_result = arithmetic_result
        elif "counting" in operation_identification.lower():
            counting_result = await self.generate(
                instruction=f"""Count occurrences:
                - Entities: {entities_numbers}
                - Target: [entity/event]
                Provide count.""",
                context=operation_identification
            )
            intermediate_result = counting_result
        elif "comparison" in operation_identification.lower():
            comparison_result = await self.generate(
                instruction=f"""Compare values:
                - Values: {entities_numbers}
                - Criteria: [greater, earlier, etc.]
                Provide comparison result.""",
                context=operation_identification
            )
            intermediate_result = comparison_result
        else:  # Span extraction
            span_extraction = await self.generate(
                instruction=f"""Extract exact text span:
                - Passage: {self.problem_text}
                - Question: [QUESTION TEXT]
                Provide span.""",
                context=operation_identification
            )
            intermediate_result = span_extraction

        # Step 5: Format and validate answer
        final_answer = await self.revise(
            instruction=f"""Format the answer appropriately:
            - Intermediate result: {intermediate_result}
            - Expected format: [number, date, text span]
            Validate and refine.""",
            context=intermediate_result
        )

        return final_answer