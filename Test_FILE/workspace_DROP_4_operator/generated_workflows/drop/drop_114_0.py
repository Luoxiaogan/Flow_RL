# Workflow ID: drop_114_0
# Benchmark: drop
# Data Indices: [164, 321]

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
        extracted_info = await self.generate(
            instruction="""Extract all named entities, numbers, dates, and relationships from the passage. 
            Format as a structured list:
            - Entities: [names, roles]
            - Numbers: [values, context]
            - Dates: [dates, associated events]
            - Relationships: [connections between entities]""",
            context=""
        )
        refined_info = await self.revise(
            instruction="Ensure all entities, numbers, and relationships are accurately identified and resolved.",
            context=extracted_info
        )

        # Step 2: Map question references to entities
        reference_mapping = await self.generate(
            instruction=f"""Map all references in the question to specific entities in the passage.
            Passage Info: {refined_info}
            Ensure pronouns and partial names are resolved correctly.""",
            context=""
        )

        # Step 3: Classify the question type
        question_type = await self.generate(
            instruction=f"""Classify the question into one of the following types:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (which is greater, which came first, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            Passage Info: {refined_info}
            Reference Mapping: {reference_mapping}""",
            context=""
        )

        # Step 4: Execute operations based on classification
        if "arithmetic" in question_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Passage Info: {refined_info}
                Reference Mapping: {reference_mapping}
                Show all steps and validate intermediate results.""",
                context=""
            )
        elif "counting" in question_type.lower():
            result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event:
                Passage Info: {refined_info}
                Reference Mapping: {reference_mapping}
                Ensure no duplicates are counted.""",
                context=""
            )
        elif "comparison" in question_type.lower():
            result = await self.generate(
                instruction=f"""Compare the specified entities based on the given criteria:
                Passage Info: {refined_info}
                Reference Mapping: {reference_mapping}
                Provide clear reasoning for the comparison.""",
                context=""
            )
        elif "span extraction" in question_type.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question:
                Passage Info: {refined_info}
                Reference Mapping: {reference_mapping}
                Ensure the span matches the passage exactly.""",
                context=""
            )
        else:
            result = await self.generate(
                instruction=f"""Solve the question using general reasoning:
                Passage Info: {refined_info}
                Reference Mapping: {reference_mapping}""",
                context=""
            )

        # Step 5: Refine and format the answer
        final_answer = await self.revise(
            instruction="Refine the result to match the expected format (number, date, or exact text span).",
            context=result
        )

        return final_answer