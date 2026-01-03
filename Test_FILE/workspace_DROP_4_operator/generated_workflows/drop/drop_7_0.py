# Workflow ID: drop_7_0
# Benchmark: drop
# Data Indices: [477, 497]

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
        initial_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, teams, places, etc.
            - Numbers: Scores, distances, times, etc.
            - Relationships: Actions, events, and connections between entities.
            Format as a structured list.""",
            context=""
        )

        # Step 2: Refine extraction to ensure completeness
        refined_extraction = await self.revise(
            instruction="Review the extracted information and add any missing details.",
            context=initial_extraction
        )

        # Step 3: Resolve references in the question
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial references in the question to specific entities in the passage:
            Passage: {refined_extraction}
            Question: [Original Problem]
            Provide a mapping of references to entities.""",
            context=refined_extraction
        )

        # Step 4: Classify the question type
        question_classification = await self.generate(
            instruction=f"""Classify the question into one of the following categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater than, less than, etc.)
            - Span Extraction (who did, what was, etc.)
            - Multi-step (requires combining multiple facts)
            Passage: {refined_extraction}
            Question: [Original Problem]
            Provide the category and reasoning.""",
            context=reference_resolution
        )

        # Step 5: Execute operations in parallel based on classification
        if "arithmetic" in question_classification.lower():
            operations = await asyncio.gather(
                self.generate(instruction="Perform addition/subtraction based on the question.", context=refined_extraction),
                self.generate(instruction="Validate the arithmetic result against the passage.", context=refined_extraction)
            )
        elif "counting" in question_classification.lower():
            operations = await asyncio.gather(
                self.generate(instruction="Count all relevant instances in the passage.", context=refined_extraction),
                self.generate(instruction="Cross-check the count for accuracy.", context=refined_extraction)
            )
        elif "comparison" in question_classification.lower():
            operations = await asyncio.gather(
                self.generate(instruction="Compare the specified values or spans.", context=refined_extraction),
                self.generate(instruction="Validate the comparison result.", context=refined_extraction)
            )
        elif "span extraction" in question_classification.lower():
            operations = await asyncio.gather(
                self.generate(instruction="Extract the exact text span from the passage.", context=refined_extraction),
                self.generate(instruction="Ensure the span matches the question requirements.", context=refined_extraction)
            )
        else:  # Multi-step reasoning
            operations = await asyncio.gather(
                self.generate(instruction="Combine multiple facts to answer the question.", context=refined_extraction),
                self.generate(instruction="Validate the multi-step reasoning.", context=refined_extraction)
            )

        # Step 6: Ensemble decision to select the best answer
        final_answer = await self.ensemble(
            instruction="""Select the best answer from the provided options:
            - Ensure the answer matches the expected format (number, date, or text span).
            - Validate against the passage and question requirements.""",
            contexts_list=operations
        )

        return final_answer