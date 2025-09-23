# Workflow ID: drop_25_0
# Benchmark: drop
# Data Indices: [381, 468]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list:
            - Entities: [names, roles]
            - Numbers: [values, context]
            - Relationships: [who did what to whom]""",
            context=""
        )

        # Step 2: Reference Resolution - Map pronouns and partial names to entities
        references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities from the passage.
            Passage entities: {initial_analysis}
            Ensure each reference maps to exactly one entity.""",
            context=initial_analysis
        )
        refined_references = await self.revise(
            instruction="Validate and refine reference mappings. Ensure no ambiguities remain.",
            context=references
        )

        # Step 3: Operation Identification - Determine the required operation(s)
        operation_identification = await self.generate(
            instruction=f"""Analyze the question to determine the required operation(s):
            - Arithmetic: addition, subtraction, etc.
            - Counting: how many times, how many different, etc.
            - Comparison: greater/longer, more, first/last, etc.
            - Span Extraction: who did, what was, when did, etc.
            Passage entities: {initial_analysis}
            Resolved references: {refined_references}""",
            context=refined_references
        )

        # Step 4: Execute Operations - Perform the identified operations
        operations = operation_identification.split("\n")
        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Execute the following operation: {op}.
                Use the passage and resolved references to compute the result.""",
                context=refined_references
            ) for op in operations if op.strip()]
        )

        # Step 5: Ensemble - Combine results and validate
        final_answer = await self.ensemble(
            instruction="""Combine results from all operations into a single coherent answer.
            Validate the answer against the passage and question requirements.
            Ensure the format matches the expected output (number, date, or text span).""",
            contexts_list=operation_results
        )

        # Step 6: Refinement - Ensure accuracy and clarity
        refined_answer = await self.revise(
            instruction="Refine the final answer for clarity, accuracy, and exact matching with the passage.",
            context=final_answer
        )

        return refined_answer