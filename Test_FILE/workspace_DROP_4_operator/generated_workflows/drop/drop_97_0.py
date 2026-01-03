# Workflow ID: drop_97_0
# Benchmark: drop
# Data Indices: [249, 231]

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

        # Step 1: Extract all relevant entities, numbers, and relationships
        extracted_info = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references (pronouns, partial names)
        reference_mapping = await self.generate(
            instruction=f"""Map all pronouns and partial names to specific entities in the passage.
            Use the following extracted information:
            {extracted_info}""",
            context=extracted_info
        )

        # Step 3: Classify the problem type
        problem_type = await self.generate(
            instruction=f"""Classify the problem type based on the question:
            - Arithmetic: Addition, subtraction, counting
            - Comparison: Greater than, less than, equal to
            - Span Extraction: Exact text spans
            Passage: {self.problem_text}
            Question: [Extract question from problem_text]""",
            context=reference_mapping
        )

        # Step 4: Execute operations based on problem type
        if "arithmetic" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operations:
                - Identify relevant numbers from the passage
                - Execute addition, subtraction, or counting as needed
                Extracted Info: {extracted_info}
                Reference Mapping: {reference_mapping}""",
                context=problem_type
            )
        elif "comparison" in problem_type.lower():
            result = await self.generate(
                instruction=f"""Compare the specified values or attributes:
                - Identify the entities or numbers to compare
                - Determine the relationship (greater than, less than, etc.)
                Extracted Info: {extracted_info}
                Reference Mapping: {reference_mapping}""",
                context=problem_type
            )
        elif "span extraction" in problem_type.lower():
            result = await self.revise(
                instruction=f"""Extract the exact text span that answers the question:
                - Ensure the span matches the passage exactly
                - Resolve any references using the mapping
                Extracted Info: {extracted_info}
                Reference Mapping: {reference_mapping}""",
                context=problem_type
            )
        else:
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                - Combine extracted information and reference mapping
                - Formulate a clear and concise answer
                Extracted Info: {extracted_info}
                Reference Mapping: {reference_mapping}""",
                context=problem_type
            )

        # Step 5: Format the answer
        final_answer = await self.summarize(
            instruction=f"""Condense the result into the expected format:
            - Number only for arithmetic
            - Exact text span for extraction
            - Clear comparison statement for comparison
            Result: {result}""",
            context=result
        )

        return final_answer