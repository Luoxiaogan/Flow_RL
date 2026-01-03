# Workflow ID: drop_108_0
# Benchmark: drop
# Data Indices: [50, 191]

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

        # Step 1: Initial Analysis - Extract entities and classify question type
        initial_analysis = await asyncio.gather(
            self.generate(
                instruction="""Extract all named entities, numbers, and relationships from the passage. 
                Format as a structured list with categories:
                - People: [names and roles]
                - Places: [locations and contexts]
                - Numbers: [values and what they represent]
                - Actions: [what happens and when]""",
                context=""
            ),
            self.generate(
                instruction="""Classify the type of question:
                - Is it arithmetic (addition, subtraction, counting)?
                - Is it a comparison (greater/less, first/last)?
                - Is it a span extraction (who, what, when)?
                Provide structured classification.""",
                context=""
            )
        )

        entities = initial_analysis[0]
        question_type = initial_analysis[1]

        # Step 2: Reference Resolution
        resolved_references = await self.revise(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities from the passage:
            Passage Entities: {entities}
            Question: [Original Problem]
            Ensure all references are unambiguous.""",
            context=question_type
        )

        # Step 3: Operation Execution
        if "arithmetic" in question_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Question: [Original Problem]
                Show all steps and provide the final answer.""",
                context=resolved_references
            )
        elif "comparison" in question_type.lower():
            result = await self.ensemble(
                instruction=f"""Compare the given options:
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Question: [Original Problem]
                Select the correct answer based on the passage.""",
                contexts_list=[entities, resolved_references]
            )
        else:  # Span extraction
            result = await self.generate(
                instruction=f"""Extract the exact text span from the passage:
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Question: [Original Problem]
                Ensure the span matches the passage exactly.""",
                context=resolved_references
            )

        # Step 4: Answer Validation
        validated_answer = await self.revise(
            instruction=f"""Validate the answer:
            Passage Entities: {entities}
            Resolved References: {resolved_references}
            Result: {result}
            Ensure the answer matches the expected format (number, date, or text span).""",
            context=result
        )

        return validated_answer