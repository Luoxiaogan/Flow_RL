# Workflow ID: drop_82_0
# Benchmark: drop
# Data Indices: [445, 33]

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
        extraction = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage:
            - Entities: Names, teams, locations, etc.
            - Numbers: Scores, statistics, dates, etc.
            - Relationships: Actions, events, and connections between entities
            Format as a structured list with clear labels.""",
            context=""
        )

        # Step 2: Resolve references (pronouns, partial names)
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to their correct referents:
            Passage: {self.problem_text}
            Extracted Information: {extraction}
            Ensure all references are unambiguous and linked to specific entities.""",
            context=extraction
        )

        # Step 3: Classify the question
        question_classification = await self.generate(
            instruction=f"""Classify the question into one of the following categories:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Greater/longer, more, earlier/later, etc.
            - Span Extraction: Who did, what was, when did, etc.
            Question: [QUESTION]
            Provide a clear classification and reasoning.""",
            context=resolved_references
        )

        # Step 4: Execute the operation based on classification
        if "arithmetic" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Extracted Information: {resolved_references}
                Question: [QUESTION]
                Show all steps and present the final numerical answer.""",
                context=resolved_references
            )
        elif "counting" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Count the required instances:
                Extracted Information: {resolved_references}
                Question: [QUESTION]
                Provide the count as a number.""",
                context=resolved_references
            )
        elif "comparison" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Compare the specified entities or values:
                Extracted Information: {resolved_references}
                Question: [QUESTION]
                State which is greater/longer/more/etc. and provide reasoning.""",
                context=resolved_references
            )
        elif "span extraction" in question_classification.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Extracted Information: {resolved_references}
                Question: [QUESTION]
                Ensure the span matches the passage exactly.""",
                context=resolved_references
            )
        else:
            result = "Unable to classify the question."

        # Step 5: Validate and finalize the result
        validated_result = await self.revise(
            instruction=f"""Validate the result against the expected format:
            Result: {result}
            Question: [QUESTION]
            Ensure the format matches (number, date, exact text span).""",
            context=result
        )

        return validated_result