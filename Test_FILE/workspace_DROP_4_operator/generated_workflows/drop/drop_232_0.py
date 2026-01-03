# Workflow ID: drop_232_0
# Benchmark: drop
# Data Indices: [350, 211]

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

        # Step 1: Initial Analysis - Extract entities and classify question
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list:
            - Entities: [names, roles, teams]
            - Numbers: [values and what they represent]
            - Relationships: [actions, events, and their participants]""",
            context=""
        )
        question_classification = await self.generate(
            instruction="""Classify the question type and identify required operations:
            - Is it arithmetic, counting, comparison, or span extraction?
            - What specific operations are needed?""",
            context=entities_extraction
        )

        # Step 2: Reference Resolution - Resolve pronouns and partial names
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities:
            Passage: {self.problem_text}
            Question: [question text]
            Entities: {entities_extraction}""",
            context=question_classification
        )

        # Step 3: Operation Execution - Perform identified operations
        operation_execution = await self.generate(
            instruction=f"""Execute the required operations based on the question:
            Passage: {self.problem_text}
            Question: [question text]
            Resolved References: {reference_resolution}
            Operations: {question_classification}""",
            context=reference_resolution
        )

        # Step 4: Validation and Formatting - Ensure answer matches expected format
        validation = await self.revise(
            instruction=f"""Validate the answer and ensure it matches the expected format:
            Passage: {self.problem_text}
            Question: [question text]
            Answer: {operation_execution}""",
            context=operation_execution
        )

        # Step 5: Ensemble Decision - Evaluate multiple candidate answers
        ensemble_decision = await self.ensemble(
            instruction="""Evaluate multiple candidate answers and select the best one:
            - Check for consistency with the passage
            - Ensure correct format and reasoning""",
            contexts_list=[operation_execution, validation]
        )

        return ensemble_decision