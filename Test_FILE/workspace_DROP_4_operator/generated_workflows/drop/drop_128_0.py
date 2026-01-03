# Workflow ID: drop_128_0
# Benchmark: drop
# Data Indices: [259, 5]

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

        # Step 1: Extract all entities, numbers, and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: Names of people, places, teams, etc.
            - Numbers: All numerical values with their context
            - Relationships: How entities and numbers are connected
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify the question type
        classification = await self.generate(
            instruction=f"""Classify the question based on the following categories:
            - Arithmetic: Addition, subtraction, max/min, etc.
            - Counting: How many times, how many different, etc.
            - Comparison: Greater/longer, less/shorter, etc.
            - Span Extraction: Who did, what was, when did, etc.
            Passage Context: {entities}
            Question: [Insert question here]
            Provide the category and reasoning.""",
            context=entities
        )

        # Step 3: Execute parallel strategies based on classification
        arithmetic_result = await self.generate(
            instruction=f"""If the question is arithmetic, perform the required operation:
            - Extract all relevant numbers
            - Perform addition, subtraction, max/min, etc.
            Passage Context: {entities}
            Question: [Insert question here]
            Provide the result with reasoning.""",
            context=entities
        )

        counting_result = await self.generate(
            instruction=f"""If the question is counting, count all relevant instances:
            - Identify the target entity or event
            - Count all occurrences
            Passage Context: {entities}
            Question: [Insert question here]
            Provide the count with reasoning.""",
            context=entities
        )

        comparison_result = await self.generate(
            instruction=f"""If the question is comparison, compare the relevant values:
            - Identify the values to compare
            - Determine greater/lesser, longer/shorter, etc.
            Passage Context: {entities}
            Question: [Insert question here]
            Provide the comparison result with reasoning.""",
            context=entities
        )

        span_result = await self.generate(
            instruction=f"""If the question is span extraction, locate the exact text:
            - Match the question to the passage
            - Extract the exact span
            Passage Context: {entities}
            Question: [Insert question here]
            Provide the span with reasoning.""",
            context=entities
        )

        # Step 4: Ensemble decision to select the best result
        final_result = await self.ensemble(
            instruction=f"""Select the best result based on the question type:
            - Arithmetic: Choose the numerical result
            - Counting: Choose the count
            - Comparison: Choose the comparison result
            - Span Extraction: Choose the exact span
            Passage Context: {entities}
            Question: [Insert question here]
            Results: 
            - Arithmetic: {arithmetic_result}
            - Counting: {counting_result}
            - Comparison: {comparison_result}
            - Span Extraction: {span_result}
            Provide the final answer with reasoning.""",
            contexts_list=[arithmetic_result, counting_result, comparison_result, span_result]
        )

        # Step 5: Validate and format the answer
        formatted_answer = await self.revise(
            instruction=f"""Validate and format the final answer:
            - Ensure it matches the expected format (number, date, text span)
            - Refine if necessary
            Final Result: {final_result}
            Question: [Insert question here]
            Provide the validated and formatted answer.""",
            context=final_result
        )

        return formatted_answer