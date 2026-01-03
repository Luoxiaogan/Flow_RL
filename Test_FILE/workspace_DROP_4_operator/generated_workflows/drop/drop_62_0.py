# Workflow ID: drop_62_0
# Benchmark: drop
# Data Indices: [228, 95]

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
        extraction = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Map question references to entities
        reference_mapping = await self.generate(
            instruction=f"""Map question references to specific entities in the passage.
            Passage entities: {extraction}
            Question: Identify pronouns, partial names, and other references in the question and resolve them to specific entities.""",
            context=extraction
        )

        # Step 3: Classify the question type
        operation_type = await self.generate(
            instruction=f"""Classify the question type based on its phrasing:
            - Arithmetic: Addition, subtraction, counting
            - Comparison: Greater/less than, earlier/later
            - Span Extraction: Exact text spans
            Entities and mappings: {reference_mapping}""",
            context=reference_mapping
        )

        # Step 4: Parallel processing for operations
        operation_result, validation = await asyncio.gather(
            self.generate(
                instruction=f"""Perform the identified operation:
                Operation type: {operation_type}
                Entities and mappings: {reference_mapping}""",
                context=reference_mapping
            ),
            self.revise(
                instruction=f"""Validate the operation result:
                Operation type: {operation_type}
                Entities and mappings: {reference_mapping}""",
                context=reference_mapping
            )
        )

        # Step 5: Synthesize and finalize the answer
        final_answer = await self.ensemble(
            instruction=f"""Select the best solution and format the answer:
            Candidate solutions: {operation_result}, {validation}
            Expected format: Number, date, or exact text span.""",
            contexts_list=[operation_result, validation]
        )

        return final_answer