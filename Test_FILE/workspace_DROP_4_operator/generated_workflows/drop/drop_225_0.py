# Workflow ID: drop_225_0
# Benchmark: drop
# Data Indices: [385, 194]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Classify the question type (counting, arithmetic, comparison, span extraction).
            Format the output as:
            - Entities: [list of entities]
            - Numbers: [list of numbers and their context]
            - Relationships: [descriptions of relationships between entities]
            - Question Type: [classification of the question]""",
            context=""
        )

        # Step 2: Parallel Processing
        entities_and_numbers = await self.generate(
            instruction="From the initial analysis, extract and organize entities and numbers.",
            context=initial_analysis
        )
        question_type = await self.generate(
            instruction="From the initial analysis, determine the specific question type and required operations.",
            context=initial_analysis
        )

        # Step 3: Operation Execution
        if "counting" in question_type.lower():
            result = await self.generate(
                instruction=f"""Count all instances of the specified event in the passage.
                Passage: {self.problem_text}
                Event: [determine from question]""",
                context=entities_and_numbers
            )
        elif "arithmetic" in question_type.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation using the extracted numbers.
                Passage: {self.problem_text}
                Operation: [determine from question]""",
                context=entities_and_numbers
            )
        elif "comparison" in question_type.lower():
            result = await self.generate(
                instruction=f"""Compare the specified entities or values based on the passage.
                Passage: {self.problem_text}
                Comparison: [determine from question]""",
                context=entities_and_numbers
            )
        else:  # Span extraction
            result = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question.
                Passage: {self.problem_text}
                Question: [use original question]""",
                context=entities_and_numbers
            )

        # Step 4: Validation and Refinement
        validated_result = await self.revise(
            instruction="Verify the result against the passage and refine if necessary.",
            context=result
        )

        # Step 5: Final Output
        final_output = await self.summarize(
            instruction="Condense the result into the required format (number, date, or text span).",
            context=validated_result
        )

        return final_output