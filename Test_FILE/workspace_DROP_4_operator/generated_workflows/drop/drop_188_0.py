# Workflow ID: drop_188_0
# Benchmark: drop
# Data Indices: [270, 424]

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
            - Entities: People, teams, locations, etc.
            - Numbers: Values and what they represent
            - Relationships: Actions, events, and associations
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references in the question
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities:
            Passage entities: {extraction}
            Question: Identify the subject and object of the query and map them to entities in the passage.""",
            context=extraction
        )

        # Step 3: Classify the question type
        classification = await self.generate(
            instruction=f"""Classify the question into one of the following types:
            - Counting: How many times..., how many different...
            - Arithmetic: Total, difference, sum, etc.
            - Comparison: Greater, longer, more, earlier, etc.
            - Span Extraction: Who did..., what was the name of...
            - Multi-step: Requires chaining multiple facts or operations
            Passage entities: {extraction}
            Resolved references: {reference_resolution}""",
            context=reference_resolution
        )

        # Step 4: Execute the required operation(s)
        if "counting" in classification.lower():
            operation_result = await self.generate(
                instruction=f"""Count the number of instances matching the query:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: Identify the target entity or event and count its occurrences.""",
                context=classification
            )
        elif "arithmetic" in classification.lower():
            operation_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: Identify the numbers and operation (addition, subtraction, etc.) and compute the result.""",
                context=classification
            )
        elif "comparison" in classification.lower():
            operation_result = await self.generate(
                instruction=f"""Compare the specified entities or values:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: Identify the entities or values to compare and determine the result.""",
                context=classification
            )
        elif "span extraction" in classification.lower():
            operation_result = await self.generate(
                instruction=f"""Extract the exact text span matching the query:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: Identify the target entity or event and extract the corresponding text span.""",
                context=classification
            )
        else:  # Multi-step
            sub_operations = await asyncio.gather(
                self.generate(
                    instruction=f"""Identify the first sub-problem:
                    Passage entities: {extraction}
                    Resolved references: {reference_resolution}
                    Question: Break down the multi-step problem into its first component.""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Identify the second sub-problem:
                    Passage entities: {extraction}
                    Resolved references: {reference_resolution}
                    Question: Break down the multi-step problem into its second component.""",
                    context=classification
                )
            )
            operation_result = await self.ensemble(
                instruction="Combine the results of the sub-problems into a unified answer.",
                contexts_list=sub_operations
            )

        # Step 5: Format the answer
        final_answer = await self.summarize(
            instruction=f"""Condense the result into the required format:
            Operation result: {operation_result}
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            context=operation_result
        )

        return final_answer