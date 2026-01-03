# Workflow ID: drop_42_0
# Benchmark: drop
# Data Indices: [193, 243]

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
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question:
            Entities extracted so far: {entities}
            Map each reference to a specific entity in the passage.""",
            context=entities
        )

        # Step 3: Identify the required operation
        operation_type = await self.generate(
            instruction=f"""Classify the question type:
            Entities and references: {resolved_references}
            Possible types:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater than, less than, etc.)
            - Span Extraction (who did, what was the name of, etc.)
            Provide the type and any specific instructions for solving.""",
            context=resolved_references
        )

        # Step 4: Conditional branching based on operation type
        if "arithmetic" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Operation details: {operation_type}
                Entities and references: {resolved_references}""",
                context=resolved_references
            )
        elif "counting" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Count the specified entities or events:
                Operation details: {operation_type}
                Entities and references: {resolved_references}""",
                context=resolved_references
            )
        elif "comparison" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Compare the specified values:
                Operation details: {operation_type}
                Entities and references: {resolved_references}""",
                context=resolved_references
            )
        elif "span extraction" in operation_type.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span:
                Operation details: {operation_type}
                Entities and references: {resolved_references}""",
                context=resolved_references
            )
        else:
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                Operation details: {operation_type}
                Entities and references: {resolved_references}""",
                context=resolved_references
            )

        # Step 5: Validate and refine the answer
        final_answer = await self.revise(
            instruction=f"""Validate the answer format and refine if necessary:
            Expected formats: number, date, or exact text span
            Current result: {result}""",
            context=result
        )

        return final_answer