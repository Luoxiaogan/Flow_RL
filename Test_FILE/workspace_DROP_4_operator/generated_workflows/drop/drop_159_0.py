# Workflow ID: drop_159_0
# Benchmark: drop
# Data Indices: [103, 26]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and classify question type
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Classify the question type into one of the following categories:
            - Arithmetic (addition, subtraction, counting)
            - Comparison (largest, shortest, etc.)
            - Span Extraction (exact text match)
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Reference Resolution - Resolve pronouns and partial names
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities in the passage.
            Use the following extracted information for context:
            {initial_analysis}
            Ensure accuracy by cross-referencing with the passage.""",
            context=initial_analysis
        )

        # Step 3: Parallel Fork - Execute operations based on question type
        if "arithmetic" in initial_analysis.lower():
            operations = ["addition", "subtraction", "counting"]
        elif "comparison" in initial_analysis.lower():
            operations = ["largest", "shortest", "earliest", "latest"]
        else:
            operations = ["span_extraction"]

        parallel_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Perform the following operation: {op}.
                Use the resolved references and extracted information:
                {resolved_references}""",
                context=resolved_references
            ) for op in operations]
        )

        # Step 4: Ensemble - Synthesize results and select the best answer
        synthesized_result = await self.ensemble(
            instruction="""Compare the results from parallel operations and select the most accurate or relevant answer.
            For span extraction tasks, ensure exact matching with the passage.""",
            contexts_list=parallel_results
        )

        # Step 5: Revise - Validate and refine the final result
        final_result = await self.revise(
            instruction="""Validate the final result for accuracy, consistency, and format.
            Refine if necessary to ensure the answer meets the expected format.""",
            context=synthesized_result
        )

        return final_result