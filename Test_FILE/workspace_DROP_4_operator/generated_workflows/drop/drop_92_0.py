# Workflow ID: drop_92_0
# Benchmark: drop
# Data Indices: [359, 271]

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

        # Step 1: Initial Analysis - Extract entities and classify the problem
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        problem_classification = await self.generate(
            instruction="""Classify this problem:
            1. Is it numerical, logical, or textual?
            2. Does it require exact calculation or estimation?
            3. Are there multiple valid approaches?
            4. What's the expected answer format?""",
            context=""
        )

        # Step 2: Parallel Processing - Resolve references and identify operation
        reference_resolution, operation_identification = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve all references in the question to specific entities in the passage:
                Passage Entities: {entities_extraction}
                Question: {{QUESTION}}""",
                context=entities_extraction
            ),
            self.generate(
                instruction=f"""Identify the required operation:
                Problem Classification: {problem_classification}
                Possible operations: addition, subtraction, counting, comparison, span extraction.""",
                context=problem_classification
            )
        )

        # Step 3: Conditional Branching - Execute the operation
        if "comparison" in operation_identification.lower():
            result = await self.generate(
                instruction=f"""Compare values to find the 'longest', 'greatest', or 'most':
                Resolved References: {reference_resolution}
                Operation: {operation_identification}""",
                context=reference_resolution
            )
        elif "counting" in operation_identification.lower():
            result = await self.generate(
                instruction=f"""Count occurrences of specific entities or events:
                Resolved References: {reference_resolution}
                Operation: {operation_identification}""",
                context=reference_resolution
            )
        elif "arithmetic" in operation_identification.lower():
            result = await self.generate(
                instruction=f"""Perform calculations using extracted numbers:
                Resolved References: {reference_resolution}
                Operation: {operation_identification}""",
                context=reference_resolution
            )
        else:  # Span extraction
            result = await self.generate(
                instruction=f"""Extract exact text spans matching the question:
                Resolved References: {reference_resolution}
                Operation: {operation_identification}""",
                context=reference_resolution
            )

        # Step 4: Validation and Synthesis
        refined_result = await self.revise(
            instruction="Refine the result to ensure accuracy and consistency.",
            context=result
        )

        final_answer = await self.ensemble(
            instruction="Synthesize multiple perspectives or validate the final answer.",
            contexts_list=[result, refined_result]
        )

        return final_answer