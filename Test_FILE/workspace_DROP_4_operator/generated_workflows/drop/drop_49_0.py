# Workflow ID: drop_49_0
# Benchmark: drop
# Data Indices: [268, 132]

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

        # Step 1: Extract key information from the passage
        extracted_info = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references and refine extracted information
        refined_info = await self.revise(
            instruction=f"""Resolve all pronouns and partial references in the question to specific entities in the passage.
            Ensure all entities in the question are correctly aligned with their counterparts in the passage.
            Original extraction: {extracted_info}""",
            context=extracted_info
        )

        # Step 3: Classify the problem type and identify required operations
        problem_type = await self.generate(
            instruction=f"""Classify this problem based on the question:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - What operations are needed (addition, subtraction, counting, comparison, span extraction)?
            Refined information: {refined_info}""",
            context=refined_info
        )

        # Step 4: Execute operations in parallel based on problem type
        if "numerical" in problem_type.lower():
            # Perform arithmetic operations
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operations (addition, subtraction, etc.) using the refined information.
                Show all steps and maintain full precision.
                Refined information: {refined_info}""",
                context=refined_info
            )
            result = arithmetic_result
        elif "span" in problem_type.lower():
            # Extract exact text span
            span_result = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question.
                Ensure the span matches the passage exactly.
                Refined information: {refined_info}""",
                context=refined_info
            )
            result = span_result
        else:
            # Default approach for other problem types
            default_result = await self.generate(
                instruction=f"""Apply general problem-solving framework based on the refined information.
                Refined information: {refined_info}""",
                context=refined_info
            )
            result = default_result

        # Step 5: Format the final answer
        final_answer = await self.summarize(
            instruction=f"""Condense the result into the required format (number, date, or exact text span).
            Ensure the answer matches the expected format and is clear and concise.
            Result: {result}""",
            context=result
        )

        return final_answer