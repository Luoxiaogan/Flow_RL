# Workflow ID: drop_149_0
# Benchmark: drop
# Data Indices: [482, 484]

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
        import re

        # Step 1: Initial Analysis and Decomposition
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Identify the question type (arithmetic, counting, comparison, span extraction).
            Resolve references (e.g., pronouns, partial names) to specific entities.
            Format the output as a structured list:
            - Entities: [names, roles]
            - Numbers: [values, what they represent]
            - Relationships: [connections between entities/numbers]
            - Question Type: [arithmetic, counting, comparison, span extraction]""",
            context=""
        )

        # Step 2: Operation Identification
        operation_identification = await self.generate(
            instruction=f"""Based on the following analysis:
            {initial_analysis}
            
            Identify the required operation(s) from the question phrasing.
            Map keywords like 'total', 'difference', 'how many' to specific operations.
            Provide a clear explanation of the reasoning.""",
            context=initial_analysis
        )
        refined_operations = await self.revise(
            instruction="Refine the operation identification to ensure accuracy.",
            context=operation_identification
        )

        # Step 3: Parallel Execution Paths
        arithmetic_result = await self.generate(
            instruction=f"""Perform arithmetic operations (addition, subtraction, etc.) using the numbers:
            {initial_analysis}
            
            Show all steps and calculations.""",
            context=refined_operations
        )
        counting_result = await self.generate(
            instruction=f"""Count occurrences of specific entities or events:
            {initial_analysis}
            
            Provide a tally and explain the reasoning.""",
            context=refined_operations
        )
        comparison_result = await self.generate(
            instruction=f"""Compare values or spans:
            {initial_analysis}
            
            Determine which is greater/longer/etc. and explain the reasoning.""",
            context=refined_operations
        )
        span_extraction_result = await self.generate(
            instruction=f"""Extract exact text spans:
            {initial_analysis}
            
            Ensure the span matches the passage exactly.""",
            context=refined_operations
        )

        # Step 4: Ensemble Decision-Making
        final_result = await self.ensemble(
            instruction="""Synthesize results from parallel analyses:
            - Arithmetic: Perform calculations.
            - Counting: Tally occurrences.
            - Comparison: Evaluate relative values.
            - Span Extraction: Match exact text.
            
            Select the most precise and canonical answer.""",
            contexts_list=[arithmetic_result, counting_result, comparison_result, span_extraction_result]
        )

        return final_result