# Workflow ID: drop_180_0
# Benchmark: drop
# Data Indices: [311, 309]

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
        
        # Phase 1: Initial Analysis
        entities_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        
        reference_resolution = await self.generate(
            instruction=f"""Resolve all references in the question to specific entities in the passage:
            Passage: {self.problem_text}
            Entities and Numbers: {entities_numbers}
            Question: [QUESTION TEXT]
            Identify and map pronouns and partial names to their referents.""",
            context=entities_numbers
        )
        
        operation_identification = await self.generate(
            instruction=f"""Classify the question type and identify required operations:
            Passage: {self.problem_text}
            Resolved References: {reference_resolution}
            Question: [QUESTION TEXT]
            Determine if the question requires counting, arithmetic, comparison, or span extraction.""",
            context=reference_resolution
        )
        
        # Phase 2: Parallel Processing
        operations = operation_identification.split("\n")
        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Execute operation: {op}
                Passage: {self.problem_text}
                Context: {reference_resolution}""",
                context=reference_resolution
            ) for op in operations if op.strip()]
        )
        
        synthesized_result = await self.ensemble(
            instruction="Synthesize results from all operations into a unified answer.",
            contexts_list=operation_results
        )
        
        # Phase 3: Validation and Refinement
        refined_answer = await self.revise(
            instruction=f"""Validate and refine the answer:
            Synthesized Result: {synthesized_result}
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            context=synthesized_result
        )
        
        return refined_answer