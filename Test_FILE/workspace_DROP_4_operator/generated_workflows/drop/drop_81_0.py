# Workflow ID: drop_81_0
# Benchmark: drop
# Data Indices: [408, 401]

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
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve question references to specific entities
        reference_resolution = await self.generate(
            instruction=f"""Map question references to specific entities in the passage:
            Passage Entities: {entities_extraction}
            Question: [QUESTION]
            Resolve pronouns and partial names to full entity names.""",
            context=entities_extraction
        )

        # Step 3: Classify the problem type and determine required operations
        problem_classification = await self.generate(
            instruction=f"""Classify the problem type and determine required operations:
            Passage: [PASSAGE]
            Question: [QUESTION]
            Resolved References: {reference_resolution}
            Identify the operation type (arithmetic, counting, comparison, span extraction) and format requirements.""",
            context=reference_resolution
        )

        # Step 4: Execute operations based on problem type
        if "arithmetic" in problem_classification.lower():
            # Perform arithmetic operations
            arithmetic_result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                Passage: [PASSAGE]
                Question: [QUESTION]
                Resolved References: {reference_resolution}
                Extract relevant numbers and compute the result.""",
                context=problem_classification
            )
            result = arithmetic_result
        elif "counting" in problem_classification.lower():
            # Count occurrences or entities
            counting_result = await self.generate(
                instruction=f"""Count occurrences or entities:
                Passage: [PASSAGE]
                Question: [QUESTION]
                Resolved References: {reference_resolution}
                Count the specified entities or events.""",
                context=problem_classification
            )
            result = counting_result
        elif "comparison" in problem_classification.lower():
            # Compare values or entities
            comparison_result = await self.generate(
                instruction=f"""Compare values or entities:
                Passage: [PASSAGE]
                Question: [QUESTION]
                Resolved References: {reference_resolution}
                Determine which is greater, longer, earlier, etc.""",
                context=problem_classification
            )
            result = comparison_result
        else:
            # Extract exact text span
            span_extraction = await self.generate(
                instruction=f"""Extract exact text span:
                Passage: [PASSAGE]
                Question: [QUESTION]
                Resolved References: {reference_resolution}
                Find the exact text span that answers the question.""",
                context=problem_classification
            )
            result = span_extraction

        # Step 5: Validate and refine the result
        validation = await self.revise(
            instruction=f"""Validate the result:
            Passage: [PASSAGE]
            Question: [QUESTION]
            Result: {result}
            Ensure the answer matches the expected format (number, date, or text span).""",
            context=result
        )

        # Step 6: Handle edge cases with ensemble
        hypotheses = await asyncio.gather(
            self.generate(instruction="Generate alternative interpretation...", context=validation),
            self.generate(instruction="Generate approximate answer...", context=validation),
            self.generate(instruction="Generate inferred answer...", context=validation)
        )
        final_answer = await self.ensemble(
            instruction="Select the most plausible answer based on passage consistency and format requirements.",
            contexts_list=hypotheses
        )

        return final_answer