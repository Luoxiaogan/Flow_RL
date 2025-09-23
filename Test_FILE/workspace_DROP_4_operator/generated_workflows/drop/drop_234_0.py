# Workflow ID: drop_234_0
# Benchmark: drop
# Data Indices: [198, 402]

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
        analysis = await self.generate(
            instruction="""Analyze the problem:
            1. Classify the question type (arithmetic, counting, comparison, span extraction, multi-step).
            2. Extract all relevant entities, numbers, and relationships from the passage.
            3. Identify any ambiguities (e.g., pronoun references) and constraints.
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Parallel Exploration
        arithmetic_branch = self.generate(
            instruction=f"""Perform arithmetic operations:
            - Extract numbers from the passage.
            - Identify required operations (addition, subtraction, etc.).
            - Calculate results based on the question.
            Context: {analysis}""",
            context=analysis
        )
        counting_branch = self.generate(
            instruction=f"""Count occurrences:
            - Identify the target entity or event.
            - Count how many times it appears in the passage.
            Context: {analysis}""",
            context=analysis
        )
        comparison_branch = self.generate(
            instruction=f"""Compare values or spans:
            - Identify items to compare.
            - Determine the comparison criteria (greater, less, equal).
            - Provide the result.
            Context: {analysis}""",
            context=analysis
        )
        span_extraction_branch = self.generate(
            instruction=f"""Extract exact text spans:
            - Identify the target phrase or sentence.
            - Ensure the span matches the passage exactly.
            Context: {analysis}""",
            context=analysis
        )

        # Run branches in parallel
        results = await asyncio.gather(
            arithmetic_branch,
            counting_branch,
            comparison_branch,
            span_extraction_branch
        )

        # Phase 3: Intermediate Validation
        validated_results = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this result: {result}",
                context=result
            ) for result in results]
        )

        # Phase 4: Synthesis
        final_answer = await self.ensemble(
            instruction="Select the best result or synthesize insights from multiple branches.",
            contexts_list=validated_results
        )

        # Phase 5: Post-Processing
        formatted_answer = await self.revise(
            instruction="""Format the final answer:
            - Ensure it matches the expected type (number, date, text span).
            - Remove unnecessary details.""",
            context=final_answer
        )

        return formatted_answer