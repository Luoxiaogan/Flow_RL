# Workflow ID: drop_164_0
# Benchmark: drop
# Data Indices: [288, 369]

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
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: Names of people, teams, players, etc.
            - Numbers: Scores, distances, counts, etc.
            - Relationships: Actions, interactions, comparisons, etc.
            Format as structured lists with clear categories.""",
            context=""
        )

        # Step 2: Classify the question type
        classification = await self.generate(
            instruction=f"""Classify the question type based on the passage and entities:
            Passage: {self.problem_text}
            Entities: {entities}
            
            Possible types:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Greater than, less than, equal to, etc.
            - Span Extraction: Who, what, when, etc.
            - Multi-step: Combines multiple operations
            
            Provide a clear classification and reasoning.""",
            context=entities
        )

        # Step 3: Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve all references in the question:
            Passage: {self.problem_text}
            Entities: {entities}
            Classification: {classification}
            
            Map pronouns, partial names, and other references to specific entities.
            Provide a mapping of references to entities.""",
            context=classification
        )

        # Step 4: Perform operations in parallel
        arithmetic_result = await self.generate(
            instruction=f"""If the question requires arithmetic operations:
            Passage: {self.problem_text}
            Entities: {entities}
            Resolved References: {resolved_references}
            
            Perform the required calculations and provide the result.""",
            context=resolved_references
        )
        counting_result = await self.generate(
            instruction=f"""If the question requires counting:
            Passage: {self.problem_text}
            Entities: {entities}
            Resolved References: {resolved_references}
            
            Count the specified items and provide the result.""",
            context=resolved_references
        )
        comparison_result = await self.generate(
            instruction=f"""If the question requires comparison:
            Passage: {self.problem_text}
            Entities: {entities}
            Resolved References: {resolved_references}
            
            Compare the specified values and provide the result.""",
            context=resolved_references
        )
        span_extraction_result = await self.generate(
            instruction=f"""If the question requires span extraction:
            Passage: {self.problem_text}
            Entities: {entities}
            Resolved References: {resolved_references}
            
            Extract the exact text span and provide the result.""",
            context=resolved_references
        )

        # Step 5: Synthesize results using ensemble
        results = [arithmetic_result, counting_result, comparison_result, span_extraction_result]
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the best answer from the following results:
            Results: {results}
            
            Select the most appropriate result based on the question type and classification.""",
            contexts_list=results
        )

        # Step 6: Format the answer
        formatted_answer = await self.revise(
            instruction=f"""Format the final answer to match the expected output:
            Final Answer: {final_answer}
            
            Ensure the format is correct (number only, date format, exact text span).""",
            context=final_answer
        )

        return formatted_answer