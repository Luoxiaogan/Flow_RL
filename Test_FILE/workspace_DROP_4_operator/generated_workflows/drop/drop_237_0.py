# Workflow ID: drop_237_0
# Benchmark: drop
# Data Indices: [306, 115]

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

        # Step 1: Extract entities, numbers, and relationships
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references (pronouns, partial names)
        resolved_references = await self.generate(
            instruction=f"""Resolve all references in the passage:
            Entities: {entities}
            Identify how pronouns and partial names map to specific entities.""",
            context=entities
        )

        # Step 3: Classify question type and identify required operations
        operation_hypotheses = await asyncio.gather(
            self.generate(
                instruction="""Classify the question type:
                - Arithmetic: Addition, subtraction, counting
                - Comparison: Greater/less than, first/last
                - Span Extraction: Exact text spans
                Identify the required operation(s).""",
                context=resolved_references
            ),
            self.generate(
                instruction="""Generate alternative interpretations of the question:
                Consider different ways the question could be understood.
                Provide multiple hypotheses for the required operation(s).""",
                context=resolved_references
            )
        )
        operation_plan = await self.ensemble(
            instruction="Select the most plausible operation plan.",
            contexts_list=operation_hypotheses
        )

        # Step 4: Execute the identified operation(s)
        execution_results = await asyncio.gather(
            self.generate(
                instruction=f"""Execute the required operation(s):
                Operation Plan: {operation_plan}
                Perform calculations or comparisons carefully.""",
                context=resolved_references
            ),
            self.revise(
                instruction=f"""Validate the execution results:
                Operation Plan: {operation_plan}
                Check for errors or missing instances.""",
                context=operation_plan
            )
        )
        validated_result = await self.ensemble(
            instruction="Synthesize validated results into a single answer.",
            contexts_list=execution_results
        )

        # Step 5: Format the answer
        final_answer = await self.revise(
            instruction=f"""Ensure the answer is formatted correctly:
            Validated Result: {validated_result}
            Match the expected format (number, date, or exact text span).""",
            context=validated_result
        )

        return final_answer