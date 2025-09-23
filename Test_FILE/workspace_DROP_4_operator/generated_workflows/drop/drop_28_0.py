# Workflow ID: drop_28_0
# Benchmark: drop
# Data Indices: [425, 273]

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

        # Step 1: Parallel Extraction of Entities, Numbers, and Relationships
        entities = await self.generate(
            instruction="""Extract all named entities (people, places, teams, etc.) and their roles.""",
            context=""
        )
        numbers = await self.generate(
            instruction="""Extract all numbers and what they represent (e.g., scores, distances, times).""",
            context=""
        )
        relationships = await self.generate(
            instruction="""Extract relationships between entities (e.g., who scored, when events occurred).""",
            context=""
        )

        # Synthesize extracted information
        synthesis = await self.ensemble(
            instruction="""Combine entities, numbers, and relationships into a coherent structure.
            Resolve any ambiguities or overlaps.""",
            contexts_list=[entities, numbers, relationships]
        )

        # Step 2: Question Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the question to determine:
            - Required operation(s) (e.g., counting, addition, comparison, span extraction)
            - Problem type (e.g., arithmetic, counting, span extraction)
            - Expected answer format (number, date, text span)""",
            context=synthesis
        )

        # Step 3: Conditional Branch Based on Problem Type
        if "count" in analysis.lower():
            # Counting Operation
            count_result = await self.generate(
                instruction=f"""Count the number of instances specified in the question.
                Ensure all instances are included and validated against the passage.
                Passage context: {synthesis}""",
                context=analysis
            )
            result = count_result
        elif "add" in analysis.lower() or "subtract" in analysis.lower():
            # Arithmetic Operation
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation (addition/subtraction).
                Extract relevant numbers and calculate the result.
                Passage context: {synthesis}""",
                context=analysis
            )
            result = arithmetic_result
        elif "compare" in analysis.lower():
            # Comparison Operation
            comparison_result = await self.generate(
                instruction=f"""Compare the specified values or spans.
                Determine which is greater/longer or which came first/last.
                Passage context: {synthesis}""",
                context=analysis
            )
            result = comparison_result
        else:
            # Span Extraction
            span_result = await self.generate(
                instruction=f"""Extract the exact text span matching the question.
                Ensure the span matches the passage exactly.
                Passage context: {synthesis}""",
                context=analysis
            )
            result = span_result

        # Step 4: Validation and Refinement
        validation = await self.revise(
            instruction="""Validate the result:
            - Check format (number, date, text span)
            - Cross-check with the passage
            - Correct any errors or inconsistencies""",
            context=result
        )

        # Final Output
        final_answer = await self.ensemble(
            instruction="""Select the best answer from the refined results.
            Ensure the answer is complete, correct, and matches the expected format.""",
            contexts_list=[result, validation]
        )

        return final_answer