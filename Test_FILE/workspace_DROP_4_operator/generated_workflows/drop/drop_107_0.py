# Workflow ID: drop_107_0
# Benchmark: drop
# Data Indices: [214, 39]

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

        # Phase 1: Initial Analysis
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - Entities: [names and roles]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=""
        )

        problem_type = await self.generate(
            instruction="""Classify the problem type and identify required operations:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span Extraction
            Provide a clear classification and reasoning.""",
            context=entities
        )

        # Phase 2: Reference Resolution
        resolved_references = await self.revise(
            instruction=f"""Resolve pronouns and partial names in the question to specific entities in the passage.
            Passage: {self.problem_text}
            Question: Extracted entities: {entities}
            Ensure all references are unambiguous.""",
            context=problem_type
        )

        # Phase 3: Operation Execution
        if "arithmetic" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Passage: {self.problem_text}
                Resolved references: {resolved_references}
                Show all steps and maintain precision.""",
                context=resolved_references
            )
        elif "counting" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Count occurrences of the specified entity or event:
                Passage: {self.problem_text}
                Resolved references: {resolved_references}
                Provide the total count.""",
                context=resolved_references
            )
        elif "comparison" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Compare the specified values or spans:
                Passage: {self.problem_text}
                Resolved references: {resolved_references}
                Determine which is greater, longer, etc.""",
                context=resolved_references
            )
        elif "span extraction" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage: {self.problem_text}
                Resolved references: {resolved_references}
                Ensure the span matches the passage exactly.""",
                context=resolved_references
            )
        else:
            result = await self.generate(
                instruction=f"""Apply a general problem-solving approach:
                Passage: {self.problem_text}
                Resolved references: {resolved_references}""",
                context=resolved_references
            )

        # Phase 4: Validation and Refinement
        validated_result = await self.revise(
            instruction=f"""Validate the result and refine if necessary:
            Passage: {self.problem_text}
            Result: {result}
            Check for accuracy, completeness, and format compliance.""",
            context=result
        )

        # Final Output
        return validated_result