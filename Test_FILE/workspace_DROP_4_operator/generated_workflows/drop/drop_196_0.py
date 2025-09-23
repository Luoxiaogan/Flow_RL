# Workflow ID: drop_196_0
# Benchmark: drop
# Data Indices: [331, 303]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all key components from the passage:
            - Entities (people, places, groups)
            - Numbers and their context
            - Relationships and actions
            - Problem type (arithmetic, comparison, span extraction, etc.)
            Provide structured output.""",
            context=""
        )

        # Step 2: Reference Resolution - Resolve pronouns and partial names
        resolved_references = await self.revise(
            instruction=f"""Resolve all ambiguous references in the passage:
            - Replace pronouns with specific entities
            - Clarify partial names
            - Ensure all entities are unambiguous
            Original Analysis: {initial_analysis}""",
            context=initial_analysis
        )

        # Step 3: Identify Required Operations - Determine what needs to be done
        operation_identification = await self.generate(
            instruction=f"""Based on the resolved references, determine the required operations:
            - Arithmetic (addition, subtraction, counting)
            - Comparison (greater than, less than)
            - Span extraction (exact text match)
            Resolved References: {resolved_references}""",
            context=resolved_references
        )

        # Step 4: Parallel Exploration - Explore multiple solution paths
        arithmetic_result = await self.generate(
            instruction=f"""Perform arithmetic operations if applicable:
            - Extract relevant numbers
            - Perform addition, subtraction, counting
            Operation Details: {operation_identification}""",
            context=resolved_references
        )
        comparison_result = await self.generate(
            instruction=f"""Perform comparison operations if applicable:
            - Compare numbers, dates, or quantities
            Operation Details: {operation_identification}""",
            context=resolved_references
        )
        span_extraction_result = await self.generate(
            instruction=f"""Extract exact text spans if applicable:
            - Match question phrasing to passage content
            Operation Details: {operation_identification}""",
            context=resolved_references
        )

        # Step 5: Ensemble - Synthesize the best result
        final_answer = await self.ensemble(
            instruction="""Select the most accurate and complete answer:
            - Validate arithmetic results
            - Confirm comparisons
            - Ensure span matches exactly
            Choose the best option.""",
            contexts_list=[arithmetic_result, comparison_result, span_extraction_result]
        )

        return final_answer