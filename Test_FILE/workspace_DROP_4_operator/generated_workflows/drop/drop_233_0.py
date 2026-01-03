# Workflow ID: drop_233_0
# Benchmark: drop
# Data Indices: [202, 147]

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

        # Step 1: Information Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Question Analysis
        question_analysis = await self.generate(
            instruction="""Analyze the question to determine its type (arithmetic, comparison, span extraction, etc.).
            Identify key phrases and classify the question type.""",
            context=entities
        )

        # Step 3: Reference Resolution
        resolved_references = await self.revise(
            instruction="""Resolve pronouns and partial names to specific entities using the extracted information.
            Ensure all references are clear and unambiguous.""",
            context=f"{entities}

{question_analysis}"
        )

        # Step 4: Operation Execution
        # Parallelize potential operations
        arithmetic_result, comparison_result, span_extraction_result = await asyncio.gather(
            self.generate(
                instruction="""If the question involves arithmetic, perform the required calculations.
                Show all steps and present the final result.""",
                context=resolved_references
            ),
            self.ensemble(
                instruction="""If the question involves comparison, compare the options and select the best one.
                Provide reasoning for the selection.""",
                contexts_list=[resolved_references, question_analysis]
            ),
            self.summarize(
                instruction="""If the question involves span extraction, extract the exact text span from the passage.
                Ensure the span matches the question requirements.""",
                context=resolved_references
            )
        )

        # Step 5: Answer Validation
        final_answer = await self.ensemble(
            instruction="""Select the most appropriate answer from the following options:
            - Arithmetic Result: {arithmetic_result}
            - Comparison Result: {comparison_result}
            - Span Extraction Result: {span_extraction_result}
            Ensure the answer matches the expected format (number, date, or text span).""",
            contexts_list=[arithmetic_result, comparison_result, span_extraction_result]
        )

        return final_answer