# Workflow ID: drop_166_0
# Benchmark: drop
# Data Indices: [11, 60]

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

        # Initial analysis to classify problem and extract entities
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify if the problem requires arithmetic, counting, comparison, or span extraction.
            2. Extract all relevant entities, numbers, and relationships.
            3. Resolve pronouns and partial names to specific entities.
            Provide structured output with categories: Problem Type, Entities, Numbers, Relationships.""",
            context=""
        )

        # Generate multiple perspectives/solution paths
        arithmetic_path = await self.generate(
            instruction=f"""If applicable, perform arithmetic operations:
            - Identify required operations (addition, subtraction, etc.)
            - Perform calculations step-by-step.
            - Validate intermediate results.
            Entities: {initial_analysis}""",
            context=initial_analysis
        )
        
        counting_path = await self.generate(
            instruction=f"""If applicable, perform counting operations:
            - Count occurrences or entities meeting specific criteria.
            - Ensure no instances are missed.
            Entities: {initial_analysis}""",
            context=initial_analysis
        )
        
        comparison_path = await self.generate(
            instruction=f"""If applicable, perform comparison operations:
            - Compare values, lengths, or sequences.
            - Determine which is greater, longer, or came first/last.
            Entities: {initial_analysis}""",
            context=initial_analysis
        )
        
        span_extraction_path = await self.generate(
            instruction=f"""If applicable, extract exact text spans:
            - Match question criteria to passage content.
            - Ensure exact matches are found.
            Entities: {initial_analysis}""",
            context=initial_analysis
        )

        # Validate and refine each path
        refined_paths = await asyncio.gather(
            self.revise(instruction="Verify arithmetic calculations and improve clarity.", context=arithmetic_path),
            self.revise(instruction="Verify counting accuracy and improve clarity.", context=counting_path),
            self.revise(instruction="Verify comparison logic and improve clarity.", context=comparison_path),
            self.revise(instruction="Verify span extraction accuracy and improve clarity.", context=span_extraction_path)
        )

        # Synthesize results into final answer
        final_answer = await self.ensemble(
            instruction="""Synthesize all validated paths into a final answer:
            - Select the most relevant path based on problem type.
            - Ensure answer matches expected format (number, date, text span).
            - Provide the final result.""",
            contexts_list=refined_paths
        )

        return final_answer