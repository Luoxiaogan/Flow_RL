# Workflow ID: drop_37_0
# Benchmark: drop
# Data Indices: [106, 360]

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

        # Step 1: Extract entities and numbers
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            Format as a structured list:
            - Entities: [names and roles]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities]""",
            context=""
        )

        # Step 2: Classify the question type
        question_type = await self.generate(
            instruction="""Classify the question type:
            - Counting/Arithmetic: Involves numbers and operations like addition/subtraction.
            - Comparison: Involves comparing values (greater, less, etc.).
            - Span Extraction: Requires extracting exact text spans.
            Provide the classification and reasoning.""",
            context=entities
        )

        # Step 3: Parallel processing based on question type
        if "counting" in question_type.lower() or "arithmetic" in question_type.lower():
            calculation = await self.generate(
                instruction=f"""Perform the required calculation based on the question:
                Entities and numbers: {entities}
                Question type: {question_type}
                Show all steps and provide the final result.""",
                context=entities
            )
            refined_result = await self.revise(
                instruction="Verify the calculation and refine if necessary.",
                context=calculation
            )
            result = refined_result

        elif "comparison" in question_type.lower():
            comparison = await self.generate(
                instruction=f"""Compare the relevant values based on the question:
                Entities and numbers: {entities}
                Question type: {question_type}
                Provide the comparison result.""",
                context=entities
            )
            refined_result = await self.revise(
                instruction="Verify the comparison and refine if necessary.",
                context=comparison
            )
            result = refined_result

        elif "span" in question_type.lower():
            span = await self.generate(
                instruction=f"""Extract the exact text span that answers the question:
                Passage: {self.problem_text}
                Question type: {question_type}
                Ensure the span matches the passage exactly.""",
                context=entities
            )
            refined_result = await self.revise(
                instruction="Verify the span extraction and refine if necessary.",
                context=span
            )
            result = refined_result

        else:
            # Fallback for unexpected question types
            result = await self.generate(
                instruction=f"""Solve the problem using general reasoning:
                Entities and numbers: {entities}
                Question type: {question_type}
                Provide the best possible answer.""",
                context=entities
            )

        # Step 4: Validate and format the final output
        final_output = await self.summarize(
            instruction="Ensure the final output matches the expected format (number, date, or exact text span).",
            context=result
        )

        return final_output