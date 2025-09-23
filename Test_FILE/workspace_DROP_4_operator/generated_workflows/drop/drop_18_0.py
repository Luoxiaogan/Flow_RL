# Workflow ID: drop_18_0
# Benchmark: drop
# Data Indices: [483, 341]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, teams, locations, etc.
            - Numbers: Values and what they represent
            - Relationships: Actions, events, and connections between entities
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.revise(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities in the passage:
            Passage Entities: {extraction}
            Question: [Original Problem]
            Ensure accurate mappings.""",
            context=extraction
        )

        # Step 3: Identify the required operation(s)
        operation_identification = await self.generate(
            instruction=f"""Identify the required operation(s) based on the question:
            Resolved References: {resolved_references}
            Question: [Original Problem]
            Map to specific operations (e.g., addition, subtraction, counting, comparison).""",
            context=resolved_references
        )

        # Step 4: Execute the operation(s)
        operation_execution = await self.revise(
            instruction=f"""Execute the identified operation(s) using the extracted data:
            Operation: {operation_identification}
            Data: {resolved_references}
            Ensure all relevant data points are included and calculations are accurate.""",
            context=operation_identification
        )

        # Step 5: Format the answer
        formatted_answer = await self.summarize(
            instruction=f"""Format the result into the required output format:
            Operation Result: {operation_execution}
            Ensure numerical answers are precise and text spans match the passage exactly.""",
            context=operation_execution
        )

        # Step 6: Error handling and refinement
        validation = await self.generate(
            instruction=f"""Validate the result:
            Formatted Answer: {formatted_answer}
            Check for errors or ambiguities and suggest corrections if needed.""",
            context=formatted_answer
        )

        if "error" in validation.lower():
            refined_answer = await self.revise(
                instruction=f"""Refine the answer based on validation feedback:
                Validation: {validation}
                Correct any issues and ensure accuracy.""",
                context=formatted_answer
            )
            return refined_answer
        else:
            return formatted_answer