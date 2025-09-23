# Workflow ID: drop_98_0
# Benchmark: drop
# Data Indices: [89, 488]

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
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Relationships: [what happens and when]""",
            context=""
        )

        # Step 2: Classify the question type
        question_classification = await self.generate(
            instruction=f"""Classify the question type based on its phrasing. 
            Possible types include:
            - Arithmetic (addition, subtraction, comparison)
            - Counting
            - Span extraction
            - Comparison
            Passage entities and numbers: {entities_extraction}""",
            context=""
        )

        # Step 3: Execute the required operation
        if "arithmetic" in question_classification.lower():
            operation_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation based on the question. 
                Extract relevant numbers from the passage and calculate the result. 
                Passage entities and numbers: {entities_extraction}""",
                context=question_classification
            )
        elif "span extraction" in question_classification.lower():
            operation_result = await self.generate(
                instruction=f"""Extract the exact text span from the passage that answers the question. 
                Ensure the span matches the passage exactly. 
                Passage entities and numbers: {entities_extraction}""",
                context=question_classification
            )
        elif "comparison" in question_classification.lower():
            operation_result = await self.generate(
                instruction=f"""Identify the target values and determine the largest, smallest, or other specified relationship. 
                Passage entities and numbers: {entities_extraction}""",
                context=question_classification
            )
        else:
            operation_result = await self.generate(
                instruction=f"""Solve the problem using general reasoning. 
                Passage entities and numbers: {entities_extraction}""",
                context=question_classification
            )

        # Step 4: Validate intermediate results
        validation = await self.revise(
            instruction="Validate the result for accuracy and completeness. Highlight any issues.",
            context=operation_result
        )

        # Step 5: Ensemble multiple candidates if needed
        final_answer = await self.ensemble(
            instruction="Select the most accurate answer from the candidates or refine further if needed.",
            contexts_list=[operation_result, validation]
        )

        return final_answer