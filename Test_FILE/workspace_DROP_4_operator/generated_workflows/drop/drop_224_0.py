# Workflow ID: drop_224_0
# Benchmark: drop
# Data Indices: [129, 347]

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
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as structured list with categories:
            - Entities: [names and roles]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=""
        )

        # Step 2: Reference Resolution
        resolved_references = await self.generate(
            instruction=f"""Map question references to specific entities in the passage:
            Passage Context: {initial_analysis}
            Question References: [pronouns, partial names, etc.]
            Provide clear mappings.""",
            context=initial_analysis
        )

        # Step 3: Operation Identification
        operation_identification = await self.generate(
            instruction=f"""Determine the required operation(s) based on the question phrasing:
            Passage Context: {initial_analysis}
            Resolved References: {resolved_references}
            Identify operations like addition, subtraction, counting, comparison, or span extraction.
            For multi-step problems, break into sub-problems.""",
            context=resolved_references
        )

        # Step 4: Parallel Execution
        operations = operation_identification.split("\n")
        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Perform the following operation:
                Operation: {op}
                Passage Context: {initial_analysis}
                Resolved References: {resolved_references}""",
                context=operation_identification
            ) for op in operations if op.strip()]
        )

        # Step 5: Validation and Refinement
        refined_results = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the result:
                Result: {res}
                Ensure accuracy and compliance with expected format.""",
                context=res
            ) for res in operation_results]
        )

        # Step 6: Ensemble for Final Output
        final_output = await self.ensemble(
            instruction="""Combine results into a final answer:
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            contexts_list=refined_results
        )

        return final_output