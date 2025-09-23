# Workflow ID: drop_201_0
# Benchmark: drop
# Data Indices: [14, 252]

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

        # Step 1: Extract all entities, numbers, and relationships
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and their relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question:
            Entities and numbers from the passage:
            {entities_and_numbers}
            Map each reference to the correct entity or number.""",
            context=entities_and_numbers
        )

        # Step 3: Classify the problem type and identify required operations
        problem_classification = await self.generate(
            instruction=f"""Classify the problem type and identify required operations:
            Passage entities and numbers:
            {entities_and_numbers}
            Resolved references:
            {resolved_references}
            Determine if the problem requires:
            - Arithmetic (addition, subtraction, etc.)
            - Counting
            - Comparison
            - Span extraction
            Provide a clear classification and reasoning.""",
            context=f"{entities_and_numbers}\n{resolved_references}"
        )

        # Step 4: Execute operations based on classification
        if "arithmetic" in problem_classification.lower():
            # Perform arithmetic operations
            calculations = await asyncio.gather(
                self.generate(
                    instruction=f"""Perform addition/subtraction based on the question:
                    Passage entities and numbers:
                    {entities_and_numbers}
                    Resolved references:
                    {resolved_references}
                    Show all steps and calculations.""",
                    context=f"{entities_and_numbers}\n{resolved_references}"
                ),
                self.generate(
                    instruction=f"""Verify the calculations independently:
                    Passage entities and numbers:
                    {entities_and_numbers}
                    Resolved references:
                    {resolved_references}
                    Cross-check the results.""",
                    context=f"{entities_and_numbers}\n{resolved_references}"
                )
            )
            result = await self.ensemble(
                instruction="Select the most consistent and accurate calculation.",
                contexts_list=calculations
            )
        elif "counting" in problem_classification.lower():
            # Perform counting operations
            count_result = await self.generate(
                instruction=f"""Count the occurrences or instances based on the question:
                Passage entities and numbers:
                {entities_and_numbers}
                Resolved references:
                {resolved_references}
                Ensure all instances are included.""",
                context=f"{entities_and_numbers}\n{resolved_references}"
            )
            result = count_result
        elif "comparison" in problem_classification.lower():
            # Perform comparison operations
            comparison_result = await self.generate(
                instruction=f"""Compare the specified entities or numbers:
                Passage entities and numbers:
                {entities_and_numbers}
                Resolved references:
                {resolved_references}
                Determine which is greater/longer/more/etc.""",
                context=f"{entities_and_numbers}\n{resolved_references}"
            )
            result = comparison_result
        elif "span extraction" in problem_classification.lower():
            # Perform span extraction
            span_result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage entities and numbers:
                {entities_and_numbers}
                Resolved references:
                {resolved_references}
                Ensure the span matches the passage exactly.""",
                context=f"{entities_and_numbers}\n{resolved_references}"
            )
            result = span_result
        else:
            # Default comprehensive approach
            result = await self.generate(
                instruction=f"""Solve the problem using a general reasoning framework:
                Passage entities and numbers:
                {entities_and_numbers}
                Resolved references:
                {resolved_references}
                Provide a clear and concise answer.""",
                context=f"{entities_and_numbers}\n{resolved_references}"
            )

        # Step 5: Format the final answer
        formatted_answer = await self.revise(
            instruction=f"""Format the answer according to the expected output:
            Raw result:
            {result}
            Ensure the answer is a number, date, or exact text span as required.""",
            context=result
        )

        return formatted_answer