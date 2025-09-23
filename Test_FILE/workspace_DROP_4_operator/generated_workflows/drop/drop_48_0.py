# Workflow ID: drop_48_0
# Benchmark: drop
# Data Indices: [294, 220]

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
            instruction="""Extract all relevant information from the passage:
            - Named entities (people, teams, places)
            - Numerical values (scores, distances, times)
            - Relationships (who did what, when, and where)
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references in the question
        reference_resolution = await self.generate(
            instruction=f"""Resolve all references in the question to specific entities in the passage:
            Passage entities: {extraction}
            Question: [Original Problem]
            Identify pronouns, partial names, and ambiguous terms.""",
            context=extraction
        )

        # Step 3: Classify the problem type
        classification = await self.generate(
            instruction=f"""Classify the problem type based on the question:
            Passage entities: {extraction}
            Resolved references: {reference_resolution}
            Question: [Original Problem]
            Categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different)
            - Comparison (greater than, less than, etc.)
            - Span extraction (who did, what was)
            - Multi-step reasoning (chaining operations)
            Provide the classification and reasoning.""",
            context=reference_resolution
        )

        # Step 4: Perform operations based on classification
        if "arithmetic" in classification.lower():
            operation_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: [Original Problem]
                Show all steps and calculations.""",
                context=classification
            )
        elif "counting" in classification.lower():
            operation_result = await self.generate(
                instruction=f"""Count the relevant instances:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: [Original Problem]
                List each instance and the total count.""",
                context=classification
            )
        elif "comparison" in classification.lower():
            operation_result = await self.generate(
                instruction=f"""Compare the relevant values:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: [Original Problem]
                Identify the greater/lesser value and explain why.""",
                context=classification
            )
        elif "span extraction" in classification.lower():
            operation_result = await self.generate(
                instruction=f"""Extract the exact text span:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: [Original Problem]
                Ensure the span matches the passage exactly.""",
                context=classification
            )
        else:  # Multi-step reasoning
            steps = await self.generate(
                instruction=f"""Break the problem into intermediate steps:
                Passage entities: {extraction}
                Resolved references: {reference_resolution}
                Question: [Original Problem]
                List each step and the required operation.""",
                context=classification
            )
            intermediate_results = await asyncio.gather(
                *[self.generate(instruction=f"Execute step: {step}", context=steps) for step in steps.split("\n")]
            )
            operation_result = await self.ensemble(
                instruction="Combine intermediate results into a final answer.",
                contexts_list=intermediate_results
            )

        # Step 5: Format the answer
        formatted_answer = await self.revise(
            instruction=f"""Ensure the answer matches the expected format:
            Operation result: {operation_result}
            Question: [Original Problem]
            Validate number format, date format, or exact text span.""",
            context=operation_result
        )

        return formatted_answer