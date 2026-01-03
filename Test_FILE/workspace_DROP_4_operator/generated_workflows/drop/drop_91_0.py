# Workflow ID: drop_91_0
# Benchmark: drop
# Data Indices: [257, 458]

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

        # Stage 1: Initial Analysis
        extract_info = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage.
            Format as structured data:
            - Entities: [names, roles, teams]
            - Numbers: [values and what they represent]
            - Relationships: [actions, events, and their participants]""",
            context=""
        )

        classify_question = await self.generate(
            instruction="""Classify the question type:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater/longer, more, first/last, etc.)
            - Span Extraction (who did, what was the name of, when did, etc.)
            Provide the classification and reasoning.""",
            context=""
        )

        # Stage 2: Reference Resolution
        resolve_references = await self.generate(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Passage: {extract_info}
            Question: {classify_question}
            Provide resolved references and reasoning.""",
            context=extract_info
        )

        validate_resolution = await self.revise(
            instruction="Validate and refine resolved references for consistency.",
            context=resolve_references
        )

        # Stage 3: Operation Execution
        if "arithmetic" in classify_question.lower():
            operation_result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                Passage: {extract_info}
                Resolved References: {validate_resolution}
                Question: {classify_question}
                Show calculations and final result.""",
                context=validate_resolution
            )
        elif "counting" in classify_question.lower():
            operation_result = await self.generate(
                instruction=f"""Count occurrences of specific events or entities:
                Passage: {extract_info}
                Resolved References: {validate_resolution}
                Question: {classify_question}
                Provide count and reasoning.""",
                context=validate_resolution
            )
        elif "comparison" in classify_question.lower():
            operation_result = await self.generate(
                instruction=f"""Compare values or spans:
                Passage: {extract_info}
                Resolved References: {validate_resolution}
                Question: {classify_question}
                Provide comparison result and reasoning.""",
                context=validate_resolution
            )
        elif "span extraction" in classify_question.lower():
            operation_result = await self.generate(
                instruction=f"""Extract exact text spans matching the question criteria:
                Passage: {extract_info}
                Resolved References: {validate_resolution}
                Question: {classify_question}
                Provide extracted spans and reasoning.""",
                context=validate_resolution
            )
        else:
            operation_result = await self.generate(
                instruction=f"""Handle unknown question type:
                Passage: {extract_info}
                Resolved References: {validate_resolution}
                Question: {classify_question}
                Provide best-effort answer and reasoning.""",
                context=validate_resolution
            )

        # Stage 4: Answer Validation and Formatting
        validate_answer = await self.revise(
            instruction="Validate the answer against question requirements and format appropriately.",
            context=operation_result
        )

        final_answer = await self.summarize(
            instruction="Condense the final result into a concise answer.",
            context=validate_answer
        )

        return final_answer