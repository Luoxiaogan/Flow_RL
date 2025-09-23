# Workflow ID: drop_109_0
# Benchmark: drop
# Data Indices: [208, 57]

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
            - Entities: People, places, organizations, etc.
            - Numbers: Quantities, dates, measurements
            - Relationships: Actions, events, cause-effect links
            Format as a structured list with categories.""",
            context=""
        )

        # Step 2: Question Understanding - Identify question type and required operations
        question_analysis = await self.generate(
            instruction=f"""Analyze the question:
            - What type of question is it? (Arithmetic, counting, comparison, span extraction)
            - What operations are required? (Addition, subtraction, comparison, etc.)
            - What format should the answer take? (Number, date, text span)
            Passage context: {initial_analysis}""",
            context=""
        )

        # Step 3: Reference Resolution - Resolve pronouns and partial names
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities:
            - Pronouns: they, he, she, it, etc.
            - Partial names: the team, the player, etc.
            Use the extracted entities: {initial_analysis}""",
            context=question_analysis
        )

        # Step 4: Operation Execution - Perform computations or extract spans
        # Parallel paths for different solution strategies
        arithmetic_result = await self.generate(
            instruction=f"""Perform arithmetic operations if required:
            - Identify all relevant numbers and their contexts
            - Execute addition, subtraction, or comparison as needed
            Context: {resolved_references}""",
            context=""
        )
        span_extraction_result = await self.generate(
            instruction=f"""Extract the exact text span that answers the question:
            - Locate the relevant sentence or phrase in the passage
            - Ensure the span matches the expected format
            Context: {resolved_references}""",
            context=""
        )

        # Step 5: Validation and Synthesis - Validate answer format and synthesize results
        final_answer = await self.ensemble(
            instruction="""Select the best answer from the provided options:
            - Validate the format (number, date, text span)
            - Choose the most accurate and complete answer
            Options:""",
            contexts_list=[arithmetic_result, span_extraction_result]
        )

        return final_answer