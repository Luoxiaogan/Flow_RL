# Workflow ID: drop_0_0
# Benchmark: drop
# Data Indices: [336, 30]

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

        # Initial analysis to classify problem and extract key entities
        initial_analysis = await self.generate(
            instruction="""Classify the problem type and extract key information:
            - Identify if the problem is numerical, logical, or textual
            - Extract all named entities, numbers, and their relationships
            - Resolve any pronouns or partial names to specific entities
            Provide structured output with clear categories.""",
            context=""
        )

        # Parallel processing for multiple potential interpretations
        entity_extraction, operation_identification = await asyncio.gather(
            self.generate(
                instruction=f"""Extract detailed information about entities:
                From the initial analysis: {initial_analysis}
                - List all entities with associated numbers
                - Resolve any ambiguous references""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Identify the required operation:
                From the initial analysis: {initial_analysis}
                - Determine if the problem requires addition, subtraction, counting, comparison, or span extraction
                - Specify the exact operation needed""",
                context=initial_analysis
            )
        )

        # Conditional branching based on identified operation
        if "subtraction" in operation_identification.lower():
            result = await self.generate(
                instruction=f"""Perform subtraction operation:
                Entities and numbers: {entity_extraction}
                Operation: {operation_identification}
                - Subtract the relevant numbers
                - Ensure all instances are considered
                Provide the final result.""",
                context=f"{entity_extraction}

{operation_identification}"
            )
        elif "addition" in operation_identification.lower():
            result = await self.generate(
                instruction=f"""Perform addition operation:
                Entities and numbers: {entity_extraction}
                Operation: {operation_identification}
                - Add the relevant numbers
                - Ensure all instances are considered
                Provide the final result.""",
                context=f"{entity_extraction}

{operation_identification}"
            )
        elif "counting" in operation_identification.lower():
            result = await self.generate(
                instruction=f"""Perform counting operation:
                Entities and numbers: {entity_extraction}
                Operation: {operation_identification}
                - Count the relevant instances
                - Ensure no instance is missed
                Provide the final count.""",
                context=f"{entity_extraction}

{operation_identification}"
            )
        elif "comparison" in operation_identification.lower():
            result = await self.generate(
                instruction=f"""Perform comparison operation:
                Entities and numbers: {entity_extraction}
                Operation: {operation_identification}
                - Compare the relevant numbers
                - Determine which is greater/lesser
                Provide the comparison result.""",
                context=f"{entity_extraction}

{operation_identification}"
            )
        else:  # Span extraction
            result = await self.generate(
                instruction=f"""Perform span extraction:
                Entities and relationships: {entity_extraction}
                Operation: {operation_identification}
                - Extract the exact text span matching the question
                Provide the extracted span.""",
                context=f"{entity_extraction}

{operation_identification}"
            )

        # Ensemble decision to select the best solution
        final_answer = await self.ensemble(
            instruction="Select the most accurate and complete answer from the provided options.",
            contexts_list=[result]
        )

        return final_answer