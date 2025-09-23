# Workflow ID: drop_89_0
# Benchmark: drop
# Data Indices: [308, 150]

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
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Named entities: People, places, organizations
            - Numbers: Values and what they represent
            - Relationships: Connections between entities and numbers
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial references in the question:
            Use the extracted information: {extraction}
            Map each reference to a specific entity or number.""",
            context=extraction
        )

        # Step 3: Classify the question type and identify the required operation
        question_analysis = await self.generate(
            instruction=f"""Classify the question type and identify the required operation:
            - Is it arithmetic (addition, subtraction, etc.)?
            - Is it counting, comparison, or span extraction?
            Use the resolved references: {resolved_references}""",
            context=resolved_references
        )

        # Step 4: Execute the operation(s) in parallel
        operation_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform addition if required:
                Use the resolved references: {resolved_references}
                Show all steps and maintain precision.""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Perform subtraction if required:
                Use the resolved references: {resolved_references}
                Show all steps and maintain precision.""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Perform counting if required:
                Use the resolved references: {resolved_references}
                Count all relevant instances.""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Perform comparison if required:
                Use the resolved references: {resolved_references}
                Compare values and determine the result.""",
                context=question_analysis
            ),
            self.generate(
                instruction=f"""Extract the exact text span if required:
                Use the resolved references: {resolved_references}
                Ensure the span matches the passage exactly.""",
                context=question_analysis
            )
        )

        # Step 5: Synthesize the results and select the best answer
        synthesized_answer = await self.ensemble(
            instruction=f"""Synthesize the results and select the best answer:
            - Operation results: {operation_results}
            - Ensure the answer matches the expected format (number, date, or exact text span).""",
            contexts_list=operation_results
        )

        # Step 6: Validate and refine the final answer
        final_answer = await self.revise(
            instruction=f"""Validate the final answer:
            - Ensure correctness and precision
            - Match the expected format
            - Address any inconsistencies.""",
            context=synthesized_answer
        )

        return final_answer