# Workflow ID: drop_145_0
# Benchmark: drop
# Data Indices: [451, 93]

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

        # Step 1: Initial Analysis - Extract Entities and Numbers
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: [names, roles, locations]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]""",
            context=""
        )

        # Step 2: Resolve References
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the passage:
            Passage context: {entities_and_numbers}
            - Map pronouns to specific entities
            - Clarify ambiguous references""",
            context=entities_and_numbers
        )

        # Step 3: Identify Operation Type
        operation_type = await self.generate(
            instruction=f"""Classify the question type based on the problem:
            Passage context: {resolved_references}
            Question types:
            - Arithmetic: Addition, subtraction, multiplication, division
            - Counting: How many times, how many different
            - Comparison: Greater than, less than, equal to
            - Span Extraction: Who did, What was, When did
            Provide a clear classification and reasoning.""",
            context=resolved_references
        )

        # Step 4: Execute Operation
        if "arithmetic" in operation_type.lower():
            # Extract relevant numbers and perform calculation
            numbers = await self.generate(
                instruction=f"""Extract all relevant numbers from the passage:
                Passage context: {resolved_references}
                Question: {operation_type}
                Identify numbers involved in the arithmetic operation.""",
                context=resolved_references
            )
            calculation = await self.generate(
                instruction=f"""Perform the arithmetic operation:
                Numbers: {numbers}
                Operation: {operation_type}
                Show all steps and provide the final result.""",
                context=numbers
            )
            result = calculation

        elif "counting" in operation_type.lower():
            # Count occurrences or entities
            count = await self.generate(
                instruction=f"""Count the required entities or events:
                Passage context: {resolved_references}
                Question: {operation_type}
                Provide the count and reasoning.""",
                context=resolved_references
            )
            result = count

        elif "comparison" in operation_type.lower():
            # Compare values or entities
            comparison = await self.generate(
                instruction=f"""Compare the specified values or entities:
                Passage context: {resolved_references}
                Question: {operation_type}
                Provide the comparison result.""",
                context=resolved_references
            )
            result = comparison

        elif "span extraction" in operation_type.lower():
            # Extract exact text span
            span = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage context: {resolved_references}
                Question: {operation_type}
                Ensure the span matches the passage exactly.""",
                context=resolved_references
            )
            result = span

        else:
            # Default approach for unclassified types
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                Passage context: {resolved_references}
                Question: {operation_type}
                Provide a clear and concise answer.""",
                context=resolved_references
            )

        # Step 5: Validate and Refine Result
        validated_result = await self.revise(
            instruction=f"""Validate the result and refine if necessary:
            Result: {result}
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            context=result
        )

        # Step 6: Final Synthesis
        final_answer = await self.ensemble(
            instruction=f"""Synthesize the final answer:
            Validated result: {validated_result}
            Select the best answer or combine insights if multiple interpretations exist.""",
            contexts_list=[result, validated_result]
        )

        return final_answer