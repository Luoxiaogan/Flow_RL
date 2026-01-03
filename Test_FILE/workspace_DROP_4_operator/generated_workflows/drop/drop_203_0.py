# Workflow ID: drop_203_0
# Benchmark: drop
# Data Indices: [21, 117]

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
        import re

        # Step 1: Extract entities and numbers
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question:
            Map them to specific entities in the passage.
            Passage Entities: {entities}""",
            context=entities
        )

        # Step 3: Classify problem type
        problem_type = await self.generate(
            instruction="""Classify the problem type based on the question:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Which is greater, which came first, etc.
            - Span Extraction: Who did, what was the name of, etc.""",
            context=resolved_references
        )

        # Step 4: Prepare data for operations
        operation_data = await self.generate(
            instruction=f"""Prepare data for the identified operation:
            Extract relevant numbers and entities.
            Problem Type: {problem_type}
            Resolved References: {resolved_references}""",
            context=resolved_references
        )

        # Step 5: Execute operation (conditional branch)
        if "arithmetic" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Perform arithmetic operation:
                - Identify numbers and operation type
                - Execute calculation
                Operation Data: {operation_data}""",
                context=operation_data
            )
        elif "comparison" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Perform comparison:
                - Identify entities or numbers to compare
                - Determine which is greater/less
                Operation Data: {operation_data}""",
                context=operation_data
            )
        elif "counting" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Count occurrences:
                - Identify target entity or event
                - Count all instances
                Operation Data: {operation_data}""",
                context=operation_data
            )
        else:  # Span extraction
            result = await self.generate(
                instruction=f"""Extract exact text span:
                - Identify target entity or phrase
                - Match exactly to passage
                Operation Data: {operation_data}""",
                context=operation_data
            )

        # Step 6: Validate and refine result
        refined_result = await self.revise(
            instruction="Verify calculations and improve clarity.",
            context=result
        )

        # Step 7: Format answer
        final_answer = await self.summarize(
            instruction="Condense result into required format (number, date, or exact text span).",
            context=refined_result
        )

        return final_answer