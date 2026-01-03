# Workflow ID: drop_43_0
# Benchmark: drop
# Data Indices: [422, 222]

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

        # Step 1: Extract all relevant information from the passage
        extracted_info = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - Entities: [names, roles, teams]
            - Numbers: [values and what they represent]
            - Actions: [events, scores, outcomes]""",
            context=""
        )

        # Step 2: Resolve references and classify the question type in parallel
        resolved_references, question_classification = await asyncio.gather(
            self.revise(
                instruction=f"""Resolve all pronouns and partial names in the passage to their corresponding entities.
                Use the following extracted information for context:
                {extracted_info}""",
                context=extracted_info
            ),
            self.generate(
                instruction="""Classify the question into one of the following categories:
                - Arithmetic: Addition, subtraction, multiplication, division
                - Counting: How many times, how many different
                - Comparison: Greater/lesser, earlier/later
                - Span Extraction: Exact text matching
                Provide the classification and specify the exact operation(s) required.""",
                context=extracted_info
            )
        )

        # Step 3: Execute the required operation(s) based on classification
        if "arithmetic" in question_classification.lower():
            operation_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation(s) using the following data:
                Extracted Information: {extracted_info}
                Question Classification: {question_classification}
                Ensure precise computation and double-check results.""",
                context=resolved_references
            )
        elif "counting" in question_classification.lower():
            operation_result = await self.generate(
                instruction=f"""Count the occurrences of the specified event using the following data:
                Extracted Information: {extracted_info}
                Question Classification: {question_classification}
                Be thorough and ensure no instances are missed.""",
                context=resolved_references
            )
        elif "comparison" in question_classification.lower():
            operation_result = await self.generate(
                instruction=f"""Compare the specified entities or values using the following data:
                Extracted Information: {extracted_info}
                Question Classification: {question_classification}
                Clearly state which is greater/lesser or earlier/later.""",
                context=resolved_references
            )
        elif "span extraction" in question_classification.lower():
            operation_result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question using the following data:
                Extracted Information: {extracted_info}
                Question Classification: {question_classification}
                Ensure the span matches the passage exactly.""",
                context=resolved_references
            )
        else:
            operation_result = await self.generate(
                instruction=f"""Solve the question using general reasoning with the following data:
                Extracted Information: {extracted_info}
                Question Classification: {question_classification}""",
                context=resolved_references
            )

        # Step 4: Format the final answer
        final_answer = await self.summarize(
            instruction=f"""Condense the result into the required format:
            Operation Result: {operation_result}
            Ensure the answer is clear, concise, and matches the expected format.""",
            context=operation_result
        )

        return final_answer