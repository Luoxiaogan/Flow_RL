# Workflow ID: drop_100_0
# Benchmark: drop
# Data Indices: [155, 160]

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

        # Step 1: Extract entities and numbers from the passage
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Analyze the question to determine its type and resolve references
        question_analysis_task = self.generate(
            instruction="""Analyze the question:
            - What type of problem is it? (arithmetic, counting, comparison, span extraction, etc.)
            - Identify all references (pronouns, partial names) and map them to entities in the passage.
            - Provide a clear classification and mapping.""",
            context=entities
        )
        question_type_task = self.generate(
            instruction="""Classify the question:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - Are there multiple valid approaches?""",
            context=""
        )
        question_analysis, question_type = await asyncio.gather(question_analysis_task, question_type_task)

        # Step 3: Execute the required operation(s) based on question type
        if "counting" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Count the relevant items:
                - Use the extracted entities: {entities}
                - Follow the question analysis: {question_analysis}
                - Ensure all instances are included.""",
                context=question_analysis
            )
        elif "arithmetic" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation:
                - Use the extracted numbers: {entities}
                - Follow the question analysis: {question_analysis}
                - Show all steps and maintain precision.""",
                context=question_analysis
            )
        elif "span extraction" in question_type.lower():
            operation_result = await self.generate(
                instruction=f"""Extract the exact text span:
                - Use the passage and question analysis: {question_analysis}
                - Ensure the span matches the passage exactly.""",
                context=question_analysis
            )
        else:
            operation_result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                - Use the extracted entities: {entities}
                - Follow the question analysis: {question_analysis}""",
                context=question_analysis
            )

        # Step 4: Validate and refine the result
        validated_result = await self.revise(
            instruction=f"""Validate the result:
            - Check for completeness and accuracy.
            - Resolve any ambiguities or errors.""",
            context=operation_result
        )

        # Step 5: Format and synthesize the final answer
        final_answer = await self.summarize(
            instruction=f"""Condense the result into the final answer:
            - Ensure the format matches the expected type (number, date, text span).
            - Match the passage exactly for span extraction.""",
            context=validated_result
        )

        return final_answer