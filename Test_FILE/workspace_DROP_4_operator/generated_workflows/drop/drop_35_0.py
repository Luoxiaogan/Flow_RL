# Workflow ID: drop_35_0
# Benchmark: drop
# Data Indices: [367, 217]

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
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Analyze the question to determine the required operation(s)
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and determine the required operation(s).
            Using the extracted information: {entities_extraction}
            Classify the question type (e.g., arithmetic, counting, comparison, span extraction).
            Identify the specific operation(s) needed to solve the problem.""",
            context=entities_extraction
        )

        # Step 3: Execute the required operation(s)
        operation_execution = await self.generate(
            instruction=f"""Execute the required operation(s) based on the analysis.
            Using the extracted information: {entities_extraction}
            And the question analysis: {question_analysis}
            Perform the operation(s) carefully and ensure all relevant instances are considered.""",
            context=question_analysis
        )

        # Step 4: Validate and refine the result
        refined_result = await self.revise(
            instruction=f"""Validate the result and refine if necessary.
            Check for completeness, accuracy, and consistency with the passage.
            Correct any errors or omissions.""",
            context=operation_execution
        )

        # Step 5: Format the final answer
        final_answer = await self.summarize(
            instruction=f"""Condense the final result into the required format.
            Ensure the answer matches the expected format (number, date, or text span).
            Final result: {refined_result}""",
            context=refined_result
        )

        return final_answer