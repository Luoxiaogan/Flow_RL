# Workflow ID: drop_5_0
# Benchmark: drop
# Data Indices: [337, 98]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, places, teams, etc.
            - Numbers: Scores, years, counts, etc.
            - Relationships: Actions, events, interactions
            Format as a structured list.""",
            context=""
        )

        # Step 2: Question Analysis - Identify the type of operation required
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and determine the required operation:
            Passage Context: {initial_analysis}
            Possible operations: Arithmetic, Counting, Comparison, Span Extraction
            Provide a clear classification and reasoning.""",
            context=self.problem_text
        )

        # Step 3: Entity Resolution - Resolve pronouns and partial names
        entity_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Passage Context: {initial_analysis}
            Question Context: {question_analysis}
            List each reference and its resolved entity.""",
            context=initial_analysis
        )

        # Step 4: Operation Execution - Perform the required operation
        operation_execution = await self.generate(
            instruction=f"""Perform the required operation based on the analysis:
            Passage Context: {initial_analysis}
            Question Context: {question_analysis}
            Resolved Entities: {entity_resolution}
            Execute the operation and provide intermediate results.""",
            context=entity_resolution
        )

        # Step 5: Validation - Validate intermediate results
        validation = await self.revise(
            instruction=f"""Validate the operation results:
            Passage Context: {initial_analysis}
            Question Context: {question_analysis}
            Operation Results: {operation_execution}
            Check for completeness and correctness.""",
            context=operation_execution
        )

        # Step 6: Answer Formatting - Format the final answer
        final_answer = await self.revise(
            instruction=f"""Format the final answer based on the question:
            Passage Context: {initial_analysis}
            Question Context: {question_analysis}
            Validated Results: {validation}
            Ensure the answer matches the expected format (number, date, or text span).""",
            context=validation
        )

        return final_answer