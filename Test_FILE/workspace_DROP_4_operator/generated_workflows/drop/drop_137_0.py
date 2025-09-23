# Workflow ID: drop_137_0
# Benchmark: drop
# Data Indices: [240, 295]

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
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )

        # Step 2: Resolve references and classify question type (parallel)
        reference_resolution, question_classification = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve all pronouns and partial names to specific entities:
                Passage Context: {extraction}
                Provide a mapping of references to entities.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Classify the question type based on its phrasing:
                Question: {self.problem_text.split('**QUESTION:**')[1].strip()}
                Categories: Arithmetic, Counting, Comparison, Span Extraction, Multi-step
                Provide reasoning for the classification.""",
                context=extraction
            )
        )

        # Step 3: Execute the required operation
        operation_result = await self.generate(
            instruction=f"""Perform the required operation based on the question type:
            Question Classification: {question_classification}
            Entities and Numbers: {extraction}
            Resolved References: {reference_resolution}
            Show all steps and provide the final result.""",
            context=f"{extraction}

{reference_resolution}

{question_classification}"
        )

        # Step 4: Validate and format the answer
        validation = await self.revise(
            instruction=f"""Validate the result against the passage and format it correctly:
            Result: {operation_result}
            Expected Format: Number, Date, or Exact Text Span
            Ensure the answer matches the expected format and is consistent with the passage.""",
            context=operation_result
        )

        # Step 5: Feedback loop (if inconsistencies are detected)
        if "inconsistent" in validation.lower() or "uncertain" in validation.lower():
            refined_result = await self.revise(
                instruction=f"""Refine the result based on detected issues:
                Issues: {validation}
                Original Data: {extraction}
                Resolved References: {reference_resolution}
                Correct errors and provide the final answer.""",
                context=validation
            )
            return refined_result

        return validation