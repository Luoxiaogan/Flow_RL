# Workflow ID: drop_242_0
# Benchmark: drop
# Data Indices: [406, 141]

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
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve all references in the question using the extracted information:
            Extracted Entities: {extraction}
            Question: [QUESTION]
            Replace pronouns and partial names with specific entities from the passage.""",
            context=extraction
        )

        # Step 3: Identify the required operation(s)
        operation_identification = await self.generate(
            instruction=f"""Classify the problem type and identify required operations:
            Extracted Entities: {extraction}
            Resolved References: {resolved_references}
            Question: [QUESTION]
            Possible operations: counting, arithmetic, comparison, span extraction.""",
            context=resolved_references
        )

        # Step 4: Execute operations (parallelize for robustness)
        async def execute_operation(operation):
            return await self.generate(
                instruction=f"""Perform the following operation:
                Operation: {operation}
                Extracted Entities: {extraction}
                Resolved References: {resolved_references}""",
                context=operation_identification
            )

        operations = ["counting", "arithmetic", "comparison", "span extraction"]
        operation_results = await asyncio.gather(*[execute_operation(op) for op in operations])

        # Step 5: Synthesize results into a final answer
        synthesis = await self.ensemble(
            instruction="""Synthesize results into a single answer:
            - Select the most relevant operation result.
            - Ensure the answer matches the expected format (number, date, or exact text span).""",
            contexts_list=operation_results
        )

        # Step 6: Refine and validate the final answer
        final_answer = await self.revise(
            instruction=f"""Refine the synthesized answer:
            Synthesis: {synthesis}
            Ensure the answer is accurate, complete, and matches the expected format.""",
            context=synthesis
        )

        return final_answer