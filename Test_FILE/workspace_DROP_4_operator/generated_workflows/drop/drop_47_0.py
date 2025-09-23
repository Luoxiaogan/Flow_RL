# Workflow ID: drop_47_0
# Benchmark: drop
# Data Indices: [312, 435]

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

        # Step 1: Parallel Extraction of Key Information
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )
        question_type_task = self.generate(
            instruction="""Classify the question type:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater, longer, etc.)
            - Span Extraction (who did, what was, etc.)""",
            context=""
        )

        entities, question_type = await asyncio.gather(entities_task, question_type_task)

        # Step 2: Dynamic Context Building Based on Question Type
        if "arithmetic" in question_type.lower():
            operation_context = await self.generate(
                instruction=f"""Identify relevant numbers and their relationships:
                Entities: {entities}
                Perform the required arithmetic operation.""",
                context=entities
            )
        elif "counting" in question_type.lower():
            operation_context = await self.generate(
                instruction=f"""Count instances based on the question:
                Entities: {entities}""",
                context=entities
            )
        elif "comparison" in question_type.lower():
            operation_context = await self.generate(
                instruction=f"""Compare values based on the question:
                Entities: {entities}""",
                context=entities
            )
        elif "span extraction" in question_type.lower():
            operation_context = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Entities: {entities}""",
                context=entities
            )
        else:
            operation_context = await self.generate(
                instruction="Handle general case with comprehensive analysis.",
                context=entities
            )

        # Step 3: Execute Operation and Validate Answer
        raw_answer = await self.generate(
            instruction=f"""Execute the required operation and provide the answer:
            Operation Context: {operation_context}""",
            context=operation_context
        )

        validated_answer = await self.revise(
            instruction=f"""Validate the answer:
            - Ensure it matches the expected format (number, date, or exact span)
            - Double-check calculations and logic
            Raw Answer: {raw_answer}""",
            context=raw_answer
        )

        return validated_answer