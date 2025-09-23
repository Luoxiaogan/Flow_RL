# Workflow ID: drop_170_0
# Benchmark: drop
# Data Indices: [370, 112]

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
            Format as a structured list:
            - People: [names and roles]
            - Teams: [team names]
            - Numbers: [values and what they represent]
            - Relationships: [who did what, when, and how]""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Map question references to specific entities in the passage.
            Passage entities: {extraction}
            Question: [QUESTION]
            Resolve pronouns and partial names to specific entities.""",
            context=extraction
        )

        # Step 3: Identify the required operation(s)
        operation_type = await self.generate(
            instruction=f"""Identify the required operation(s) based on the question.
            Passage entities: {extraction}
            Resolved references: {resolved_references}
            Question: [QUESTION]
            Possible operations: addition, subtraction, comparison, counting, span extraction.
            Output the operation type and any necessary parameters.""",
            context=resolved_references
        )

        # Step 4: Execute the operation(s)
        if "addition" in operation_type.lower():
            candidates = await asyncio.gather(
                self.generate(instruction="Perform addition using extracted numbers...", context=operation_type),
                self.generate(instruction="Double-check addition for accuracy...", context=operation_type)
            )
            result = await self.ensemble(
                instruction="Select the most accurate result.",
                contexts_list=candidates
            )
        elif "subtraction" in operation_type.lower():
            candidates = await asyncio.gather(
                self.generate(instruction="Perform subtraction using extracted numbers...", context=operation_type),
                self.generate(instruction="Validate subtraction with alternative method...", context=operation_type)
            )
            result = await self.ensemble(
                instruction="Select the most accurate result.",
                contexts_list=candidates
            )
        elif "comparison" in operation_type.lower():
            candidates = await asyncio.gather(
                self.generate(instruction="Compare values and determine the larger/smaller...", context=operation_type),
                self.generate(instruction="Cross-check comparison logic...", context=operation_type)
            )
            result = await self.ensemble(
                instruction="Select the most accurate result.",
                contexts_list=candidates
            )
        elif "span extraction" in operation_type.lower():
            result = await self.generate(
                instruction="Extract the exact text span from the passage that answers the question...",
                context=operation_type
            )
        else:
            result = await self.generate(
                instruction="Handle unknown operation type with general reasoning...",
                context=operation_type
            )

        # Step 5: Format the answer
        formatted_answer = await self.summarize(
            instruction="Format the answer to match the expected output. Numerical answers should be numbers only. Text spans should match the passage exactly.",
            context=result
        )

        return formatted_answer