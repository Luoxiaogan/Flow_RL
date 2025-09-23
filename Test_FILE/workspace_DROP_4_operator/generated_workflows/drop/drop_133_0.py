# Workflow ID: drop_133_0
# Benchmark: drop
# Data Indices: [131, 165]

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

        # Step 1: Initial Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as structured list with categories: People, Places, Numbers, Actions.""",
            context=""
        )

        # Step 2: Reference Resolution
        references = await self.generate(
            instruction="""Identify and resolve all references in the question to specific entities in the passage. 
            Provide a mapping of references to entities.""",
            context=entities
        )

        # Step 3: Operation Classification
        operation_type = await self.generate(
            instruction="""Classify the question into one of the following types: Arithmetic, Counting, Comparison, Span Extraction. 
            Provide reasoning for the classification.""",
            context=f"{entities}\n{references}"
        )

        # Step 4: Parallel Operations
        if "arithmetic" in operation_type.lower():
            tasks = [
                self.generate(instruction="Perform addition if required...", context=operation_type),
                self.generate(instruction="Perform subtraction if required...", context=operation_type),
                self.generate(instruction="Perform comparison if required...", context=operation_type)
            ]
        elif "counting" in operation_type.lower():
            tasks = [
                self.generate(instruction="Count occurrences of specific entities...", context=operation_type),
                self.generate(instruction="Count unique entities...", context=operation_type)
            ]
        elif "comparison" in operation_type.lower():
            tasks = [
                self.generate(instruction="Compare numerical values...", context=operation_type),
                self.generate(instruction="Compare textual spans...", context=operation_type)
            ]
        elif "span extraction" in operation_type.lower():
            tasks = [
                self.generate(instruction="Extract exact text spans matching criteria...", context=operation_type)
            ]
        else:
            tasks = [
                self.generate(instruction="Generate general solution approach...", context=operation_type)
            ]

        parallel_results = await asyncio.gather(*tasks)

        # Step 5: Ensemble Synthesis
        synthesized_result = await self.ensemble(
            instruction="Synthesize results from different analyses into a single coherent answer. Ensure consistency and accuracy.",
            contexts_list=parallel_results
        )

        # Step 6: Final Revision
        final_answer = await self.revise(
            instruction="Format the answer according to the expected output. Ensure clarity and correctness.",
            context=synthesized_result
        )

        return final_answer