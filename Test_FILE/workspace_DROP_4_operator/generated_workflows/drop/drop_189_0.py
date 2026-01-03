# Workflow ID: drop_189_0
# Benchmark: drop
# Data Indices: [365, 68]

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
        
        # Step 1: Classify the problem type
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Arithmetic (addition, subtraction, etc.)
            - Counting (how many times, how many different, etc.)
            - Comparison (greater than, less than, etc.)
            - Span Extraction (exact text match)
            - Multi-step (combination of the above)
            Provide a clear classification and reasoning.""",
            context=""
        )
        
        # Step 2: Extract entities and numbers
        entities_and_numbers = await self.generate(
            instruction=f"""Extract all named entities, numbers, and relationships from the passage.
            Format as:
            - Entities: [names, roles, descriptions]
            - Numbers: [values and their context]
            - Relationships: [connections between entities/numbers]""",
            context=classification
        )
        
        # Step 3: Parallel processing based on classification
        if "arithmetic" in classification.lower():
            # Arithmetic path
            arithmetic_result = await self.generate(
                instruction=f"""Perform the required arithmetic operation using the extracted numbers:
                {entities_and_numbers}
                Operation: [addition/subtraction/etc.]""",
                context=entities_and_numbers
            )
            candidate_answers = [arithmetic_result]
        
        elif "counting" in classification.lower():
            # Counting path
            counting_result = await self.generate(
                instruction=f"""Count the occurrences of the specified entity/event:
                {entities_and_numbers}""",
                context=entities_and_numbers
            )
            candidate_answers = [counting_result]
        
        elif "comparison" in classification.lower():
            # Comparison path
            comparison_result = await self.generate(
                instruction=f"""Compare the specified values/attributes:
                {entities_and_numbers}""",
                context=entities_and_numbers
            )
            candidate_answers = [comparison_result]
        
        elif "span extraction" in classification.lower():
            # Span extraction path
            span_result = await self.generate(
                instruction=f"""Identify the exact text span matching the question:
                {entities_and_numbers}""",
                context=entities_and_numbers
            )
            candidate_answers = [span_result]
        
        else:  # Multi-step or uncertain classification
            # Spawn exploratory branches
            arithmetic_result = await self.generate(
                instruction=f"""Attempt arithmetic reasoning:
                {entities_and_numbers}""",
                context=entities_and_numbers
            )
            counting_result = await self.generate(
                instruction=f"""Attempt counting reasoning:
                {entities_and_numbers}""",
                context=entities_and_numbers
            )
            comparison_result = await self.generate(
                instruction=f"""Attempt comparison reasoning:
                {entities_and_numbers}""",
                context=entities_and_numbers
            )
            span_result = await self.generate(
                instruction=f"""Attempt span extraction:
                {entities_and_numbers}""",
                context=entities_and_numbers
            )
            candidate_answers = [arithmetic_result, counting_result, comparison_result, span_result]
        
        # Step 4: Validate and revise intermediate results
        revised_answers = await asyncio.gather(
            *[self.revise(
                instruction="Validate and improve clarity of this result.",
                context=answer
            ) for answer in candidate_answers]
        )
        
        # Step 5: Ensemble decision
        final_answer = await self.ensemble(
            instruction="Select the most accurate and complete answer.",
            contexts_list=revised_answers
        )
        
        return final_answer