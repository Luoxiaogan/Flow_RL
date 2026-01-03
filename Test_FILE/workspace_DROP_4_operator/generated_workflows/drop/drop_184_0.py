# Workflow ID: drop_184_0
# Benchmark: drop
# Data Indices: [107, 437]

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
        entities_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and their relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Classify question type
        question_type = await self.generate(
            instruction=f"""Classify the question type based on the following:
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times, occurrences, etc.
            - Comparison: Greater than, less than, etc.
            - Span Extraction: Exact text spans
            - Multi-step: Combining multiple operations
            
            Passage Context: {entities_numbers}""",
            context=""
        )

        # Step 3: Parallel reasoning paths
        arithmetic_result = await self.generate(
            instruction=f"""Perform arithmetic operations if applicable:
            - Identify relevant numbers from: {entities_numbers}
            - Execute addition, subtraction, etc. based on question: {question_type}""",
            context=""
        )

        counting_result = await self.generate(
            instruction=f"""Count occurrences if applicable:
            - Identify target entities or events from: {entities_numbers}
            - Count based on question: {question_type}""",
            context=""
        )

        comparison_result = await self.generate(
            instruction=f"""Compare values if applicable:
            - Identify values to compare from: {entities_numbers}
            - Compare based on question: {question_type}""",
            context=""
        )

        span_extraction_result = await self.generate(
            instruction=f"""Extract exact text spans if applicable:
            - Identify relevant spans from: {entities_numbers}
            - Match spans to question: {question_type}""",
            context=""
        )

        multi_step_result = await self.generate(
            instruction=f"""Chain multiple operations if applicable:
            - Combine steps from: {entities_numbers}
            - Follow logic in question: {question_type}""",
            context=""
        )

        # Step 4: Ensemble synthesis
        final_answer = await self.ensemble(
            instruction="""Evaluate and select the best answer:
            - Ensure consistency with passage and question
            - Choose the most accurate and complete response""",
            contexts_list=[
                arithmetic_result,
                counting_result,
                comparison_result,
                span_extraction_result,
                multi_step_result
            ]
        )

        return final_answer