# Workflow ID: drop_138_0
# Benchmark: drop
# Data Indices: [133, 301]

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

        # Step 1: Extract all relevant entities, numbers, and relationships
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, places, organizations
            - Numbers: All numerical values with their context
            - Relationships: How entities are related to each other
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references to specific entities
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Given entities: {entities_extraction}
            Map each pronoun and partial name to its corresponding entity.""",
            context=entities_extraction
        )

        # Step 3: Identify the required operation(s)
        operation_identification = await self.generate(
            instruction=f"""Identify the required operation(s) from the question:
            Given entities and resolved references: {reference_resolution}
            Determine if the question requires addition, subtraction, counting, comparison, or span extraction.
            Provide a clear explanation of the identified operation(s).""",
            context=reference_resolution
        )

        # Step 4: Execute the identified operations
        execution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Execute the identified operations:
                Operations: {operation_identification}
                Perform the calculations or extractions as specified.""",
                context=operation_identification
            ),
            self.generate(
                instruction=f"""Provide an alternative execution path:
                Operations: {operation_identification}
                Consider different interpretations or methods.""",
                context=operation_identification
            )
        )

        # Step 5: Validate and refine the results
        refined_results = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the result:
                Original result: {attempt}
                Correct any errors and add missing details.""",
                context=attempt
            ) for attempt in execution_attempts]
        )

        # Step 6: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the refined results:
            Evaluate each result based on accuracy, completeness, and adherence to the expected format.
            Select the best solution or merge insights if necessary.""",
            contexts_list=refined_results
        )

        return final_solution