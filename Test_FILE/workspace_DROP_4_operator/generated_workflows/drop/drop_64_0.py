# Workflow ID: drop_64_0
# Benchmark: drop
# Data Indices: [473, 374]

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
            instruction="""Extract all named entities, numbers, and relationships:
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        # Step 2: Classify the problem type
        classification = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            - Arithmetic: Requires addition, subtraction, etc.
            - Counting: Requires tallying occurrences.
            - Comparison: Requires evaluating relative values.
            - Span Extraction: Requires matching exact text spans.
            Provide a clear classification and reasoning.""",
            context=entities
        )
        
        # Step 3: Conditional branching based on problem type
        if "arithmetic" in classification.lower():
            # Perform arithmetic operations
            operations = await self.generate(
                instruction=f"""Identify and perform the required arithmetic operations:
                Entities and relationships: {entities}
                Classification: {classification}
                Show all steps and calculations.""",
                context=entities
            )
            result = operations
        
        elif "counting" in classification.lower():
            # Perform counting
            count = await self.generate(
                instruction=f"""Count the required occurrences:
                Entities and relationships: {entities}
                Classification: {classification}
                Provide the total count.""",
                context=entities
            )
            result = count
        
        elif "comparison" in classification.lower():
            # Perform comparison
            comparison = await self.generate(
                instruction=f"""Compare the specified values:
                Entities and relationships: {entities}
                Classification: {classification}
                State which is greater/longer/etc.""",
                context=entities
            )
            result = comparison
        
        elif "span extraction" in classification.lower():
            # Perform span extraction
            span = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Entities and relationships: {entities}
                Classification: {classification}
                Ensure the span matches the passage exactly.""",
                context=entities
            )
            result = span
        
        else:
            # Default approach for unclassified problems
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                Entities and relationships: {entities}
                Classification: {classification}
                Provide a detailed solution.""",
                context=entities
            )
        
        # Step 4: Validate and format the answer
        validated_answer = await self.revise(
            instruction="""Validate the answer and format it appropriately:
            - Ensure the format matches the expected type (number, date, text span).
            - Double-check calculations and references.
            - Present the final answer clearly.""",
            context=result
        )
        
        return validated_answer