# Workflow ID: drop_45_0
# Benchmark: drop
# Data Indices: [423, 167]

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

        # Phase 1: Extraction
        extracted_info = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Phase 2: Resolution
        resolved_references = await self.revise(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Extracted Info: {extracted_info}
            Map 'they', 'the team', etc., to their corresponding entities.""",
            context=extracted_info
        )

        # Phase 3: Operation Identification
        operation_identification = await self.generate(
            instruction=f"""Classify the problem type and identify required operations:
            Extracted Info: {extracted_info}
            Resolved References: {resolved_references}
            Determine if the problem involves arithmetic, counting, comparison, or span extraction.
            Specify the exact operation(s) needed.""",
            context=resolved_references
        )

        # Phase 4: Execution
        execution_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform the identified operations:
                Operations: {operation_identification}
                Execute calculations, comparisons, or span extraction as specified.""",
                context=operation_identification
            ),
            self.revise(
                instruction=f"""Validate intermediate results:
                Operations: {operation_identification}
                Check for errors or inconsistencies.""",
                context=operation_identification
            )
        )
        executed_result, validation_result = execution_results

        # Phase 5: Validation
        final_answer = await self.ensemble(
            instruction="""Select the best answer that matches the expected format:
            Ensure the answer is a number, date, or exact text span as required.""",
            contexts_list=[executed_result, validation_result]
        )

        return final_answer