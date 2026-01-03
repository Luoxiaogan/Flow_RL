# Workflow ID: drop_44_0
# Benchmark: drop
# Data Indices: [417, 377]

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

        # Step 1: Initial Analysis and Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and classify it:
            - Is it numerical, textual, or comparative?
            - Does it require arithmetic operations, counting, or span extraction?
            - Identify key entities, numbers, and relationships.
            Provide a structured analysis.""",
            context=""
        )

        # Step 2: Entity and Relationship Extraction
        entities = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Based on the analysis: {initial_analysis}""",
            context=""
        )

        # Step 3: Reference Resolution
        resolved_references = await self.generate(
            instruction=f"""Resolve question references to specific entities:
            - Map pronouns and partial names to their full forms.
            - Cross-reference with extracted entities: {entities}
            Ensure all references are unambiguous.""",
            context=entities
        )

        # Step 4: Operation Identification and Execution
        operation_identification = await self.generate(
            instruction=f"""Identify the required operation(s) from the question phrasing:
            - Addition: 'total', 'sum'
            - Subtraction: 'more', 'difference'
            - Comparison: 'greater', 'longer'
            - Counting: 'how many times', 'how many different'
            Based on the resolved references: {resolved_references}""",
            context=resolved_references
        )

        # Execute operations in parallel for robustness
        operations = ["addition", "subtraction", "comparison", "counting"]
        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Execute {op} operation based on the identified requirements:
                - Use extracted numbers and relationships: {entities}
                - Ensure all instances are considered.""",
                context=operation_identification
            ) for op in operations]
        )

        # Step 5: Answer Formatting and Validation
        best_answer = await self.ensemble(
            instruction="""Select the best answer from the executed operations:
            - Ensure the answer matches the expected format (number, date, text span).
            - Validate against the passage for exact match.""",
            contexts_list=operation_results
        )

        final_answer = await self.revise(
            instruction=f"""Refine the selected answer:
            - Ensure it matches the passage exactly.
            - Format appropriately (number only, date format, exact text span).
            Final validation: {best_answer}""",
            context=best_answer
        )

        return final_answer