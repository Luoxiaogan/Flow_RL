# Workflow ID: drop_115_0
# Benchmark: drop
# Data Indices: [496, 244]

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

        # Step 1: Initial Extraction
        extracted_info = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Parallel Analysis
        classification, operation_identification = await asyncio.gather(
            self.generate(
                instruction="Classify the problem type: arithmetic, counting, comparison, or span extraction.",
                context=extracted_info
            ),
            self.generate(
                instruction="Identify required operations: addition, subtraction, counting, comparison, etc.",
                context=extracted_info
            )
        )

        # Step 3: Operation Execution
        if "arithmetic" in classification.lower():
            result = await self.generate(
                instruction=f"""Perform arithmetic operations:
                - Use numbers from: {operation_identification}
                - Show all steps and maintain precision.""",
                context=extracted_info
            )
        elif "span extraction" in classification.lower():
            result = await self.generate(
                instruction=f"""Extract exact text span:
                - Match question to passage content.
                - Ensure precision and format.""",
                context=extracted_info
            )
        else:
            result = await self.generate(
                instruction="Apply general problem-solving framework.",
                context=extracted_info
            )

        # Step 4: Validation and Feedback
        validation = await self.generate(
            instruction="Validate result against expected format: number, date, or text span.",
            context=result
        )
        if "error" in validation.lower():
            result = await self.revise(
                instruction="Refine output based on validation feedback.",
                context=result
            )

        # Step 5: Final Synthesis
        final_answer = await self.ensemble(
            instruction="Synthesize validated outputs into a single coherent answer.",
            contexts_list=[result, validation]
        )

        return final_answer