# Workflow ID: drop_136_0
# Benchmark: drop
# Data Indices: [126, 418]

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
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - Entities: People, places, teams, etc.
            - Numbers: Values with units or context
            - Relationships: Connections between entities and numbers
            Format as structured list.""",
            context=""
        )

        # Step 2: Resolve references
        resolved_references = await self.revise(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Passage: {self.problem_text}
            Extracted entities: {entities_and_numbers}
            Identify which entity each reference points to.""",
            context=entities_and_numbers
        )

        # Step 3: Identify required operation
        operation_identification = await self.generate(
            instruction=f"""Analyze the question and determine the required operation:
            Question: {self.problem_text.split('QUESTION:')[1].split('ANSWER:')[0].strip()}
            Possible operations: counting, sorting, arithmetic, span extraction
            Specify exact operation and parameters.""",
            context=resolved_references
        )

        # Step 4: Execute operation
        operation_execution = await self.generate(
            instruction=f"""Execute the identified operation using the extracted data:
            Operation: {operation_identification}
            Data: {resolved_references}
            Validate intermediate results and ensure correctness.""",
            context=operation_identification
        )

        # Step 5: Format answer
        answer_formatting = await self.revise(
            instruction=f"""Format the final answer according to the expected output type:
            Operation result: {operation_execution}
            Expected format: number, date, or exact text span
            Ensure precision and match original text if applicable.""",
            context=operation_execution
        )

        # Optional refinement loop
        refined_answer = answer_formatting
        for _ in range(2):  # Allow up to 2 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the answer:
                Answer: {refined_answer}
                Original problem: {self.problem_text}
                Identify any issues or ambiguities.""",
                context=refined_answer
            )
            if "error" in validation.lower() or "ambiguous" in validation.lower():
                refined_answer = await self.revise(
                    instruction=f"""Refine the answer based on validation feedback:
                    Validation: {validation}
                    Current answer: {refined_answer}""",
                    context=refined_answer
                )
            else:
                break

        return refined_answer