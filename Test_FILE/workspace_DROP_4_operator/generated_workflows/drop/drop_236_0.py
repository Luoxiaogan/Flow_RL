# Workflow ID: drop_236_0
# Benchmark: drop
# Data Indices: [204, 0]

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

        # Step 1: Extract all entities, numbers, dates, and relationships from the passage
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, dates, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references in the question to specific entities in the passage
        reference_resolution = await self.generate(
            instruction=f"""Resolve any references in the question to specific entities in the passage.
            Passage Entities: {entities_extraction}
            Question: [Extracted Question from problem_text]
            Identify pronouns, partial names, and other references and map them to specific entities.""",
            context=entities_extraction
        )

        # Step 3: Identify the type of operation required by the question
        operation_identification = await self.generate(
            instruction=f"""Identify the type of operation required by the question.
            Passage Entities: {entities_extraction}
            Resolved References: {reference_resolution}
            Question: [Extracted Question from problem_text]
            Classify the question into one of the following operations:
            - Counting
            - Addition/Subtraction
            - Comparison
            - Span Extraction
            Provide reasoning for the classification.""",
            context=reference_resolution
        )

        # Step 4: Execute parallel operations based on the identified operation
        # Parallel branches for different types of operations
        counting_result = await self.generate(
            instruction=f"""If the operation is counting, count the occurrences of the relevant entities.
            Passage Entities: {entities_extraction}
            Resolved References: {reference_resolution}
            Question: [Extracted Question from problem_text]
            Provide the count and reasoning.""",
            context=operation_identification
        )

        arithmetic_result = await self.generate(
            instruction=f"""If the operation is arithmetic, perform the required calculations.
            Passage Entities: {entities_extraction}
            Resolved References: {reference_resolution}
            Question: [Extracted Question from problem_text]
            Show all steps and provide the final result.""",
            context=operation_identification
        )

        comparison_result = await self.generate(
            instruction=f"""If the operation is comparison, compare the relevant values.
            Passage Entities: {entities_extraction}
            Resolved References: {reference_resolution}
            Question: [Extracted Question from problem_text]
            Provide the comparison result and reasoning.""",
            context=operation_identification
        )

        span_extraction_result = await self.generate(
            instruction=f"""If the operation is span extraction, extract the exact text span.
            Passage Entities: {entities_extraction}
            Resolved References: {reference_resolution}
            Question: [Extracted Question from problem_text]
            Provide the exact text span and reasoning.""",
            context=operation_identification
        )

        # Step 5: Ensemble decision to synthesize results from parallel operations
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the results from the parallel operations into a final answer.
            Counting Result: {counting_result}
            Arithmetic Result: {arithmetic_result}
            Comparison Result: {comparison_result}
            Span Extraction Result: {span_extraction_result}
            Select the most appropriate result based on the question and provide the final answer.""",
            contexts_list=[counting_result, arithmetic_result, comparison_result, span_extraction_result]
        )

        # Step 6: Final answer formatting
        formatted_answer = await self.revise(
            instruction=f"""Ensure the final answer is formatted correctly.
            Final Answer: {final_answer}
            Format the answer as a number, date, or exact text span as required by the question.""",
            context=final_answer
        )

        return formatted_answer