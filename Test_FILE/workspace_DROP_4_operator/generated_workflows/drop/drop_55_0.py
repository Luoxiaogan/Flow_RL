# Workflow ID: drop_55_0
# Benchmark: drop
# Data Indices: [431, 149]

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

        # Step 1: Extract entities and numbers
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to specific entities.
            Entities extracted: {entities_extraction}
            Provide a mapping of references to entities.""",
            context=entities_extraction
        )

        # Step 3: Identify required operation
        operation_identification = await self.generate(
            instruction=f"""Identify the required operation based on the question.
            Entities and references: {reference_resolution}
            Possible operations: addition, subtraction, counting, comparison, span extraction.
            Provide the operation and relevant numbers/entities.""",
            context=reference_resolution
        )

        # Step 4: Generate multiple solution attempts
        attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Attempt 1: Solve using the identified operation.
                Operation: {operation_identification}
                Show all steps and calculations.""",
                context=operation_identification
            ),
            self.generate(
                instruction=f"""Attempt 2: Solve using an alternative interpretation.
                Operation: {operation_identification}
                Consider different reference resolutions or operations.""",
                context=operation_identification
            )
        )

        # Step 5: Revise and validate attempts
        revised_attempts = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and improve clarity of the solution.
                Ensure all steps are correct and complete.""",
                context=attempt
            ) for attempt in attempts]
        )

        # Step 6: Ensemble to select the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Accuracy of calculations
            - Clarity of reasoning
            - Match with expected answer format""",
            contexts_list=revised_attempts
        )

        return final_solution