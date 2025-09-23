# Workflow ID: drop_104_0
# Benchmark: drop
# Data Indices: [77, 276]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Named entities: People, places, organizations
            - Numbers: Values and what they represent
            - Relationships: How entities and numbers are connected
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Classify the problem type
        problem_type = await self.generate(
            instruction=f"""Classify the problem based on the question:
            - Arithmetic: Involves addition, subtraction, multiplication, division
            - Counting: Requires tallying occurrences
            - Comparison: Asks for greater, smaller, or meets criteria
            - Span Extraction: Requires exact text spans
            Use the extracted information:
            {extracted_info}
            Provide a clear classification.""",
            context=extracted_info
        )

        # Step 3: Branch based on problem type
        if "arithmetic" in problem_type.lower():
            # Perform arithmetic operations
            solution_attempt = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Identify the numbers involved
                - Determine the operation (addition, subtraction, etc.)
                - Show the calculation steps
                - Provide the final result
                Use the extracted information:
                {extracted_info}""",
                context=extracted_info
            )
        elif "counting" in problem_type.lower():
            # Count occurrences
            solution_attempt = await self.generate(
                instruction=f"""Count the occurrences of the specified entity or event:
                - Identify the target entity or event
                - Tally the instances in the passage
                - Provide the total count
                Use the extracted information:
                {extracted_info}""",
                context=extracted_info
            )
        elif "comparison" in problem_type.lower():
            # Compare values
            solution_attempt = await self.generate(
                instruction=f"""Compare the specified values:
                - Identify the values to compare
                - Determine the comparison criteria (greater, smaller, etc.)
                - Provide the result of the comparison
                Use the extracted information:
                {extracted_info}""",
                context=extracted_info
            )
        elif "span extraction" in problem_type.lower():
            # Extract exact text span
            solution_attempt = await self.generate(
                instruction=f"""Locate the exact text span that answers the question:
                - Identify the relevant part of the passage
                - Ensure the span matches the question's requirements
                - Provide the exact text span
                Use the extracted information:
                {extracted_info}""",
                context=extracted_info
            )
        else:
            # Default approach for unclassified problems
            solution_attempt = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                - Analyze the question and passage
                - Identify the required information
                - Provide a clear and concise answer
                Use the extracted information:
                {extracted_info}""",
                context=extracted_info
            )

        # Step 4: Revise the solution attempt
        revised_solution = await self.revise(
            instruction="""Critique and refine the solution:
            - Check for accuracy and completeness
            - Fix any errors or inconsistencies
            - Adjust the format to match the expected output
            - Provide the improved solution""",
            context=solution_attempt
        )

        # Step 5: Summarize the final answer
        final_answer = await self.summarize(
            instruction="""Condense the solution into a concise answer:
            - Ensure the answer is clear and accurate
            - Match the expected format (number, date, text span)
            - Provide the final result""",
            context=revised_solution
        )

        return final_answer