# Workflow ID: drop_163_0
# Benchmark: drop
# Data Indices: [58, 23]

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

        # Step 1: Extract Information
        extracted_info = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: Names, places, organizations, etc.
            - Numbers: All numerical values and their context
            - Relationships: Connections between entities and numbers
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve References
        reference_mapping = await self.generate(
            instruction=f"""Map pronouns and partial names to specific entities:
            Passage: {extracted_info}
            Create a mapping of references to entities.""",
            context=extracted_info
        )
        resolved_references = await self.revise(
            instruction="Ensure all references are correctly mapped to entities.",
            context=reference_mapping
        )

        # Step 3: Identify Operations
        operation_identification = await self.generate(
            instruction=f"""Analyze the question to determine the required operation(s):
            Passage: {resolved_references}
            Question types:
            - Arithmetic: Addition, subtraction, counting
            - Comparison: Greater than, less than
            - Span Extraction: Exact text spans
            Identify the operation(s) needed to answer the question.""",
            context=resolved_references
        )

        # Step 4: Execute Operations
        operation_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform addition operations:
                {operation_identification}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Perform subtraction operations:
                {operation_identification}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Perform counting operations:
                {operation_identification}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Perform comparison operations:
                {operation_identification}""",
                context=resolved_references
            )
        )

        # Step 5: Format Answer
        formatted_answer = await self.summarize(
            instruction="Condense the results into a single answer matching the expected format.",
            context="\n".join(operation_results)
        )
        final_answer = await self.revise(
            instruction="Ensure the answer is correctly formatted and matches the expected output.",
            context=formatted_answer
        )

        return final_answer