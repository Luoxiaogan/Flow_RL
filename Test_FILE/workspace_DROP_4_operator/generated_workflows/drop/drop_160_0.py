# Workflow ID: drop_160_0
# Benchmark: drop
# Data Indices: [99, 242]

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

        # Step 1: Initial Analysis - Extract all relevant entities and numbers
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Reference Mapping - Map question references to specific entities
        reference_mapping = await self.generate(
            instruction=f"""Map question references to specific entities in the passage:
            Passage Entities: {entities_extraction}
            Question: [QUESTION]
            Resolve pronouns and partial names to their corresponding entities.""",
            context=entities_extraction
        )

        # Step 3: Question Classification - Classify the question type
        question_classification = await self.generate(
            instruction=f"""Classify the question type based on its phrasing:
            Passage: [PASSAGE]
            Question: [QUESTION]
            Possible types: arithmetic, counting, comparison, span extraction, multi-step
            Provide detailed reasoning for the classification.""",
            context=reference_mapping
        )

        # Step 4: Operation Execution - Perform necessary calculations or comparisons
        operation_execution = await self.generate(
            instruction=f"""Based on the question type: {question_classification}
            Perform the necessary calculations or comparisons:
            - Arithmetic: Perform addition, subtraction, etc.
            - Counting: Count occurrences of specific entities or events
            - Comparison: Compare values or entities
            - Span Extraction: Extract exact text spans from the passage
            Ensure accuracy and completeness.""",
            context=question_classification
        )

        # Step 5: Answer Formatting - Format the answer appropriately
        answer_formatting = await self.revise(
            instruction=f"""Format the answer to match the expected output format:
            Operation Result: {operation_execution}
            Expected formats: number only, date format, exact text span
            Ensure the answer is clear and concise.""",
            context=operation_execution
        )

        # Step 6: Validation and Refinement - Validate and refine the answer
        final_answer = await self.revise(
            instruction=f"""Validate the answer and refine if necessary:
            Formatted Answer: {answer_formatting}
            Check for accuracy, completeness, and correct formatting.""",
            context=answer_formatting
        )

        return final_answer