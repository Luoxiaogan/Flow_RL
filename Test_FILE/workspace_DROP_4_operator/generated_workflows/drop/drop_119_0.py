# Workflow ID: drop_119_0
# Benchmark: drop
# Data Indices: [172, 206]

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

        # --- ANALYSIS PHASE ---
        # Extract entities, numbers, and relationships
        extraction = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage:
            - Entities: People, places, organizations, etc.
            - Numbers: Include units and what they represent
            - Relationships: How entities are connected
            Format as a structured list.""",
            context=""
        )

        # Resolve references and clarify ambiguities
        resolved = await self.revise(
            instruction="""Resolve any ambiguous references (e.g., pronouns, partial names) 
            to specific entities. Clarify relationships if needed.""",
            context=extraction
        )

        # Classify the problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the question:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Greater than, less than, first/last, etc.
            - Span Extraction: Who did, what was, when did, etc.
            Problem context: {resolved}""",
            context=""
        )

        # --- EXECUTION PHASE ---
        # Dynamically branch based on problem type
        if "arithmetic" in classification.lower():
            # Identify relevant numbers and perform calculation
            numbers = await self.generate(
                instruction=f"""Identify all relevant numbers and their roles in the calculation.
                Context: {resolved}""",
                context=""
            )
            result = await self.revise(
                instruction=f"""Perform the required arithmetic operation:
                - Show all steps
                - Maintain precision
                Numbers: {numbers}""",
                context=resolved
            )
        elif "counting" in classification.lower():
            # Count occurrences of specific entities or events
            result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event.
                Context: {resolved}""",
                context=""
            )
        elif "comparison" in classification.lower():
            # Compare values or spans
            candidates = await asyncio.gather(
                self.generate(instruction="Extract value/span A...", context=resolved),
                self.generate(instruction="Extract value/span B...", context=resolved)
            )
            result = await self.ensemble(
                instruction="Compare the two values/spans and determine the answer.",
                contexts_list=candidates
            )
        elif "span extraction" in classification.lower():
            # Extract exact text span
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question.
                Context: {resolved}""",
                context=""
            )
        else:
            # Default approach for unclassified problems
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning.
                Context: {resolved}""",
                context=""
            )

        # --- VALIDATION PHASE ---
        # Validate the answer format and logical consistency
        validated = await self.revise(
            instruction="""Ensure the answer matches the expected format:
            - Number only
            - Date format
            - Exact text span
            Validate logical consistency with the passage.""",
            context=result
        )

        return validated