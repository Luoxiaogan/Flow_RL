# Workflow ID: drop_112_0
# Benchmark: drop
# Data Indices: [266, 109]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Classify the problem type (numerical, textual, logical).
            2. Extract all named entities, numbers, and relationships from the passage.
            3. Identify key constraints and conditions in the question.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Processing
        reference_resolution, operation_identification, span_extraction = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve references and map question terms to passage entities:
                Problem Analysis: {initial_analysis}
                Focus on resolving pronouns, partial names, and ambiguous terms.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Identify required operations:
                Problem Analysis: {initial_analysis}
                Determine if the question requires addition, subtraction, comparison, or other operations.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Extract candidate text spans:
                Problem Analysis: {initial_analysis}
                Focus on exact matches for span-based questions.""",
                context=initial_analysis
            )
        )

        # Step 3: Conditional Branching
        if "numerical" in initial_analysis.lower():
            # Execute arithmetic operations
            arithmetic_result = await self.generate(
                instruction=f"""Perform the identified arithmetic operations:
                Operations: {operation_identification}
                Use numbers and relationships from: {reference_resolution}""",
                context=operation_identification
            )
            final_result = arithmetic_result
        elif "textual" in initial_analysis.lower():
            # Select best span using ensemble
            best_span = await self.ensemble(
                instruction=f"""Select the best text span:
                Candidates: {span_extraction}
                Criteria: Exact match, relevance to question.""",
                contexts_list=span_extraction.split("\n")
            )
            final_result = best_span
        else:
            # Default comprehensive approach
            final_result = await self.generate(
                instruction=f"""Solve using general reasoning:
                Analysis: {initial_analysis}
                Resolved References: {reference_resolution}
                Identified Operations: {operation_identification}
                Extracted Spans: {span_extraction}""",
                context=initial_analysis
            )

        # Step 4: Iterative Refinement
        validation = await self.generate(
            instruction=f"""Validate the solution:
            Final Result: {final_result}
            Check for errors, inconsistencies, or missing details.""",
            context=final_result
        )
        if "error" in validation.lower():
            refined_result = await self.revise(
                instruction=f"""Revise the solution based on validation feedback:
                Feedback: {validation}
                Original Result: {final_result}""",
                context=final_result
            )
            final_result = refined_result

        return final_result