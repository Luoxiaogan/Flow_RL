# Workflow ID: drop_200_0
# Benchmark: drop
# Data Indices: [382, 265]

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

        # Step 1: Extract all entities, numbers, and relationships
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, places, organizations, etc.
            - Numbers: All numerical values and what they represent
            - Relationships: How entities and numbers are connected""",
            context=""
        )

        # Step 2: Resolve references (pronouns, partial names)
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the passage to specific entities:
            Passage: {entities_and_numbers}
            Ensure each reference is mapped to the correct entity.""",
            context=entities_and_numbers
        )

        # Step 3: Identify the required operation(s) from the question
        operation_identification = await self.generate(
            instruction=f"""Analyze the question and identify the required operation(s):
            Passage: {entities_and_numbers}
            Resolved References: {reference_resolution}
            Classify the problem type (arithmetic, counting, comparison, span extraction) and specify the operation(s).""",
            context=reference_resolution
        )

        # Step 4: Execute the identified operation(s)
        if "count" in operation_identification.lower():
            # Counting operation
            count_result = await self.generate(
                instruction=f"""Count all relevant instances in the passage:
                Passage: {entities_and_numbers}
                Operation: {operation_identification}""",
                context=operation_identification
            )
            result = count_result
        elif "arithmetic" in operation_identification.lower():
            # Arithmetic operation
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Passage: {entities_and_numbers}
                Operation: {operation_identification}""",
                context=operation_identification
            )
            result = arithmetic_result
        elif "comparison" in operation_identification.lower():
            # Comparison operation
            comparison_result = await self.generate(
                instruction=f"""Compare the relevant values in the passage:
                Passage: {entities_and_numbers}
                Operation: {operation_identification}""",
                context=operation_identification
            )
            result = comparison_result
        else:
            # Span extraction
            span_extraction = await self.generate(
                instruction=f"""Extract the exact text span from the passage:
                Passage: {entities_and_numbers}
                Operation: {operation_identification}""",
                context=operation_identification
            )
            result = span_extraction

        # Step 5: Validate and refine the result
        refined_result = await self.revise(
            instruction=f"""Validate and refine the result:
            Original Result: {result}
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            context=result
        )

        # Step 6: Return the final answer
        return refined_result