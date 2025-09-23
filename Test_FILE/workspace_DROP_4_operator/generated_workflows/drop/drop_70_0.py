# Workflow ID: drop_70_0
# Benchmark: drop
# Data Indices: [137, 466]

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

        # Step 1: Initial Analysis - Extract structured information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all relevant entities, numbers, and relationships from the passage. 
            Classify the problem type as one of the following:
            - Arithmetic (addition, subtraction, etc.)
            - Comparison (greater/less than, ranges, etc.)
            - Counting (occurrences, entities, etc.)
            - Span Extraction (exact text match)
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Branching - Process based on problem type
        arithmetic_result = await self.generate(
            instruction=f"""If the problem is arithmetic, perform the required calculations using the extracted data:
            {initial_analysis}
            Validate the result against the passage.""",
            context=initial_analysis
        )
        comparison_result = await self.generate(
            instruction=f"""If the problem is a comparison, compare the relevant values or ranges:
            {initial_analysis}
            Ensure the comparison aligns with the passage.""",
            context=initial_analysis
        )
        counting_result = await self.generate(
            instruction=f"""If the problem involves counting, count the occurrences or entities:
            {initial_analysis}
            Verify the count against the passage.""",
            context=initial_analysis
        )
        span_extraction_result = await self.generate(
            instruction=f"""If the problem requires span extraction, identify the exact text span:
            {initial_analysis}
            Ensure the span matches the passage exactly.""",
            context=initial_analysis
        )

        # Step 3: Validation - Revise intermediate results
        validated_arithmetic = await self.revise(
            instruction="Validate the arithmetic result and correct any errors.",
            context=arithmetic_result
        )
        validated_comparison = await self.revise(
            instruction="Validate the comparison result and correct any errors.",
            context=comparison_result
        )
        validated_counting = await self.revise(
            instruction="Validate the counting result and correct any errors.",
            context=counting_result
        )
        validated_span = await self.revise(
            instruction="Validate the span extraction result and correct any errors.",
            context=span_extraction_result
        )

        # Step 4: Ensemble Synthesis - Select the best result
        final_result = await self.ensemble(
            instruction="Select the most accurate and relevant result based on validation criteria.",
            contexts_list=[
                validated_arithmetic,
                validated_comparison,
                validated_counting,
                validated_span
            ]
        )

        # Step 5: Final Output - Format the answer
        formatted_answer = await self.summarize(
            instruction="Condense the final result into the required format (number, date, or text span).",
            context=final_result
        )

        return formatted_answer