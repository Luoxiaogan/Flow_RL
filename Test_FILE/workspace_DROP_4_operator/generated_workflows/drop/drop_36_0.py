# Workflow ID: drop_36_0
# Benchmark: drop
# Data Indices: [79, 210]

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

        # Step 1: Extract entities, numbers, and relationships
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage and question.
            - Named entities: People, places, organizations, etc.
            - Numbers: Values and what they represent
            - Relationships: Actions, events, and connections between entities
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify problem type
        classification = await self.generate(
            instruction=f"""Classify the problem type based on the extracted information:
            {extraction}
            
            Categories:
            - Arithmetic: Addition, subtraction, multiplication, division
            - Counting: How many times, how many different, etc.
            - Comparison: Greater than, less than, equal to, etc.
            - Span Extraction: Exact text spans from the passage
            Provide a clear classification and reasoning.""",
            context=extraction
        )

        # Step 3: Generate parallel solution attempts
        arithmetic_solution = await self.generate(
            instruction=f"""If this is an arithmetic problem, solve it using the following steps:
            {classification}
            
            Steps:
            - Identify the operation (addition, subtraction, etc.)
            - Perform the calculation carefully
            - Present the final answer with appropriate units.""",
            context=extraction
        )

        counting_solution = await self.generate(
            instruction=f"""If this is a counting problem, solve it using the following steps:
            {classification}
            
            Steps:
            - Identify the target entity or event
            - Count occurrences accurately
            - Present the final count.""",
            context=extraction
        )

        comparison_solution = await self.generate(
            instruction=f"""If this is a comparison problem, solve it using the following steps:
            {classification}
            
            Steps:
            - Identify the values or spans to compare
            - Perform the comparison (greater than, less than, etc.)
            - Present the result clearly.""",
            context=extraction
        )

        span_extraction_solution = await self.generate(
            instruction=f"""If this is a span extraction problem, solve it using the following steps:
            {classification}
            
            Steps:
            - Identify the exact text span matching the question
            - Ensure the span matches the passage exactly
            - Present the extracted span.""",
            context=extraction
        )

        # Step 4: Validate and refine solutions
        refined_arithmetic = await self.revise(
            instruction="Validate and refine the arithmetic solution.",
            context=arithmetic_solution
        )

        refined_counting = await self.revise(
            instruction="Validate and refine the counting solution.",
            context=counting_solution
        )

        refined_comparison = await self.revise(
            instruction="Validate and refine the comparison solution.",
            context=comparison_solution
        )

        refined_span = await self.revise(
            instruction="Validate and refine the span extraction solution.",
            context=span_extraction_solution
        )

        # Step 5: Ensemble decision
        final_answer = await self.ensemble(
            instruction="Select the best solution based on validation and alignment with the question.",
            contexts_list=[
                refined_arithmetic,
                refined_counting,
                refined_comparison,
                refined_span
            ]
        )

        return final_answer