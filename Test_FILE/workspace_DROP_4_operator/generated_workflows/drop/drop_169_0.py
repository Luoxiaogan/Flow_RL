# Workflow ID: drop_169_0
# Benchmark: drop
# Data Indices: [168, 166]

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

        # Step 1: Initial Analysis
        extraction_task = self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage:
            - Entities: Names of people, teams, places, etc.
            - Numbers: All numerical values and their context (e.g., '30-yard field goal')
            - Relationships: How entities and numbers are connected (e.g., 'Carney made a 29-yard field goal')
            Format as a structured list.""",
            context=""
        )

        classification_task = self.generate(
            instruction="""Classify the question type:
            - Is it arithmetic (addition, subtraction, etc.)?
            - Is it counting (how many times, how many different)?
            - Is it comparison (greater, longer, earlier)?
            - Is it span extraction (who did, what was)?
            Provide a clear classification.""",
            context=""
        )

        # Run initial tasks in parallel
        extraction, classification = await asyncio.gather(extraction_task, classification_task)

        # Step 2: Parallel Streams
        reference_resolution = self.generate(
            instruction=f"""Resolve all references in the question:
            - Map pronouns and partial names to specific entities in the passage.
            Passage entities: {extraction}
            Question: [Question from problem]
            Provide a mapping of references to entities.""",
            context=extraction
        )

        operation_preparation = self.generate(
            instruction=f"""Prepare data for the required operation:
            - Based on the question type: {classification}
            - Identify relevant numbers and entities from: {extraction}
            - Prepare inputs for the operation (e.g., summing field goal yards).""",
            context=extraction
        )

        # Run parallel streams
        resolved_references, prepared_data = await asyncio.gather(reference_resolution, operation_preparation)

        # Step 3: Conditional Execution
        if "arithmetic" in classification.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Data: {prepared_data}
                - Operation: [Addition/Subtraction/etc. based on question]
                Show all steps and provide the final result.""",
                context=prepared_data
            )
        elif "counting" in classification.lower():
            result = await self.generate(
                instruction=f"""Count the required instances:
                - Data: {prepared_data}
                - What to count: [Specific entities/events based on question]
                Provide the total count.""",
                context=prepared_data
            )
        elif "comparison" in classification.lower():
            result = await self.generate(
                instruction=f"""Compare the specified values:
                - Data: {prepared_data}
                - What to compare: [Entities/Numbers based on question]
                State which is greater/longer/earlier/etc.""",
                context=prepared_data
            )
        elif "span extraction" in classification.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span:
                - Passage: [Passage from problem]
                - Question: [Question from problem]
                Provide the exact matching span.""",
                context=resolved_references
            )
        else:
            result = await self.generate(
                instruction="Apply a general reasoning approach to solve the problem.",
                context=prepared_data
            )

        # Step 4: Result Synthesis
        final_answer = await self.ensemble(
            instruction="""Synthesize the results:
            - Combine outputs from all streams.
            - Ensure the answer matches the expected format (number, date, text span).
            - If necessary, refine the answer for clarity and correctness.""",
            contexts_list=[resolved_references, prepared_data, result]
        )

        return final_answer