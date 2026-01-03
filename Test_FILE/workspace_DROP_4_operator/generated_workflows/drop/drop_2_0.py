# Workflow ID: drop_2_0
# Benchmark: drop
# Data Indices: [290, 32]

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

        # Step 1: Initial Analysis - Extract entities and classify question type
        initial_analysis = await self.generate(
            instruction="""Extract all entities, numbers, and relationships from the passage. 
            Classify the question type into one of the following categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater than, less than, etc.)
            - Span Extraction (who did, what was, etc.)
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Processing - Handle different question types
        entities_and_numbers = await self.generate(
            instruction="Extract all entities and numbers from the passage.",
            context=initial_analysis
        )
        question_type = await self.generate(
            instruction="Classify the question type based on the initial analysis.",
            context=initial_analysis
        )

        # Spawn parallel branches based on question type
        if "arithmetic" in question_type.lower():
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation using the extracted numbers:
                Passage Numbers: {entities_and_numbers}
                Question: {self.problem_text}""",
                context=entities_and_numbers
            )
            result = arithmetic_result

        elif "counting" in question_type.lower():
            counting_result = await self.generate(
                instruction=f"""Count the occurrences of the specified event or entity:
                Entities: {entities_and_numbers}
                Question: {self.problem_text}""",
                context=entities_and_numbers
            )
            result = counting_result

        elif "comparison" in question_type.lower():
            comparison_result = await self.generate(
                instruction=f"""Compare the specified values or spans:
                Entities: {entities_and_numbers}
                Question: {self.problem_text}""",
                context=entities_and_numbers
            )
            result = comparison_result

        elif "span extraction" in question_type.lower():
            span_extraction_result = await self.generate(
                instruction=f"""Identify and validate the exact text span that answers the question:
                Entities: {entities_and_numbers}
                Question: {self.problem_text}""",
                context=entities_and_numbers
            )
            result = span_extraction_result

        else:
            result = "Unable to classify question type."

        # Step 3: Validation and Refinement
        refined_result = await self.revise(
            instruction="Validate the result and refine if necessary.",
            context=result
        )

        # Step 4: Final Synthesis
        final_answer = await self.ensemble(
            instruction="Select the best answer based on validation and refinement.",
            contexts_list=[result, refined_result]
        )

        return final_answer