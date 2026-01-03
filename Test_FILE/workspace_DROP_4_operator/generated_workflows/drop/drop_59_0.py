# Workflow ID: drop_59_0
# Benchmark: drop
# Data Indices: [218, 499]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as structured data:
            - Entities: [names, roles, descriptions]
            - Numbers: [values, units, what they represent]
            - Relationships: [connections between entities/numbers]""",
            context=""
        )

        # Step 2: Resolve references in the question
        reference_resolution = await self.revise(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities in the passage. 
            Passage entities: {extraction}
            Question: [original question]""",
            context=extraction
        )

        # Step 3: Classify the question type and identify required operations
        classification = await self.generate(
            instruction=f"""Classify the question type and identify required operations:
            - Is it numerical (addition, subtraction, etc.)?
            - Does it involve counting, comparison, or span extraction?
            Passage entities: {extraction}
            Resolved references: {reference_resolution}""",
            context=reference_resolution
        )

        # Step 4: Execute operations based on classification
        if "numerical" in classification.lower():
            # Compute multiple interpretations in parallel
            candidates = await asyncio.gather(
                self.generate(
                    instruction=f"""Perform addition/subtraction based on the question:
                    Passage entities: {extraction}
                    Resolved references: {reference_resolution}""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Perform alternative computation (e.g., rephrasing the question):
                    Passage entities: {extraction}
                    Resolved references: {reference_resolution}""",
                    context=classification
                )
            )
        elif "counting" in classification.lower():
            candidates = await asyncio.gather(
                self.generate(
                    instruction=f"""Count instances based on the question:
                    Passage entities: {extraction}
                    Resolved references: {reference_resolution}""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Alternative counting method (e.g., grouping):
                    Passage entities: {extraction}
                    Resolved references: {reference_resolution}""",
                    context=classification
                )
            )
        else:
            # Default to span extraction
            candidates = await asyncio.gather(
                self.generate(
                    instruction=f"""Extract exact text span matching the question:
                    Passage entities: {extraction}
                    Resolved references: {reference_resolution}""",
                    context=classification
                ),
                self.generate(
                    instruction=f"""Alternative span extraction (e.g., rephrasing):
                    Passage entities: {extraction}
                    Resolved references: {reference_resolution}""",
                    context=classification
                )
            )

        # Step 5: Validate and select the best result
        final_result = await self.ensemble(
            instruction="""Select the most accurate and valid answer:
            - Ensure numerical answers match expected format
            - Validate span extractions against the passage
            - Choose the most precise interpretation""",
            contexts_list=candidates
        )

        return final_result