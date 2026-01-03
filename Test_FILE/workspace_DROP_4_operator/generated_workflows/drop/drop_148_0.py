# Workflow ID: drop_148_0
# Benchmark: drop
# Data Indices: [96, 460]

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

        # Step 1: Extract entities and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Analyze the question and identify the required operation
        operation = await self.generate(
            instruction=f"""Analyze the question and classify it into one of the following categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (which is greater, which came first, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            Passage entities and relationships: {entities}""",
            context=""
        )

        # Step 3: Resolve references in the question
        resolved_references = await self.revise(
            instruction=f"""Resolve any pronouns or partial names in the question to specific entities from the passage.
            Passage entities and relationships: {entities}
            Question: {operation}""",
            context=operation
        )

        # Step 4: Execute the operation
        execution_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform the required operation based on the question analysis.
                Passage entities and relationships: {entities}
                Resolved references: {resolved_references}""",
                context=resolved_references
            ),
            self.generate(
                instruction=f"""Validate the operation by cross-checking with the passage.
                Passage entities and relationships: {entities}
                Resolved references: {resolved_references}""",
                context=resolved_references
            )
        )

        # Step 5: Format and validate the answer
        final_answer = await self.ensemble(
            instruction=f"""Select the best answer from the execution results.
            Ensure the answer matches the expected format (number, date, or exact text span).
            Execution results: {execution_results}""",
            contexts_list=execution_results
        )

        return final_answer