# Workflow ID: drop_58_0
# Benchmark: drop
# Data Indices: [364, 372]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Classify the problem type:
            - Is it arithmetic, counting, comparison, span extraction, or multi-step reasoning?
            - What is the expected answer format (number, date, text span)?
            Provide structured classification.""",
            context=""
        )

        # Step 2: Information Extraction
        extracted_info = await self.generate(
            instruction=f"""Extract all relevant entities, numbers, and relationships:
            - Entities: [names, roles, locations]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities and numbers]
            Based on problem analysis: {analysis}""",
            context=""
        )

        # Step 3: Operation Identification
        operation_plan = await self.generate(
            instruction=f"""Identify required operations based on problem type:
            - Arithmetic: Addition, subtraction, multiplication
            - Counting: Tally instances
            - Comparison: Sorting, inequalities
            - Span extraction: Exact matches
            Extracted info: {extracted_info}
            Problem analysis: {analysis}""",
            context=extracted_info
        )

        # Step 4: Execution and Validation
        # Parallel execution of operations
        operation_results = await asyncio.gather(
            self.generate(
                instruction=f"""Execute arithmetic operations:
                - Perform calculations step-by-step
                - Double-check intermediate results
                Plan: {operation_plan}""",
                context=extracted_info
            ),
            self.generate(
                instruction=f"""Perform counting:
                - Tally instances carefully
                - Ensure no duplicates or omissions
                Plan: {operation_plan}""",
                context=extracted_info
            ),
            self.generate(
                instruction=f"""Conduct comparisons:
                - Sort values
                - Evaluate inequalities
                Plan: {operation_plan}""",
                context=extracted_info
            ),
            self.generate(
                instruction=f"""Extract text spans:
                - Find exact matches in the passage
                - Validate against original text
                Plan: {operation_plan}""",
                context=extracted_info
            )
        )

        # Step 5: Ensemble and Final Answer
        final_answer = await self.ensemble(
            instruction="""Select the best solution:
            - Ensure answer matches expected format
            - Validate against problem requirements
            - Handle ambiguity by selecting most plausible option""",
            contexts_list=operation_results
        )

        return final_answer