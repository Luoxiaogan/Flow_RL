# Workflow ID: drop_31_0
# Benchmark: drop
# Data Indices: [366, 161]

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
        entities_extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            Format as a structured list:
            - Entities: [names, roles]
            - Numbers: [values, what they represent]
            - Relationships: [connections between entities]""",
            context=""
        )

        # Step 2: Resolve references (pronouns, partial names)
        reference_resolution = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question and passage:
            Passage: {self.problem_text}
            Entities: {entities_extraction}
            
            Map each reference to a specific entity.""",
            context=entities_extraction
        )

        # Step 3: Classify the question and identify the required operation
        question_classification = await self.generate(
            instruction=f"""Classify the question and identify the required operation:
            Passage: {self.problem_text}
            Resolved References: {reference_resolution}
            
            Determine the operation type (arithmetic, counting, comparison, span extraction) and any hidden reasoning steps.""",
            context=reference_resolution
        )

        # Step 4: Perform the identified operation
        operation_execution = await self.generate(
            instruction=f"""Perform the identified operation:
            Passage: {self.problem_text}
            Resolved References: {reference_resolution}
            Operation Type: {question_classification}
            
            Execute the operation step-by-step and show all calculations.""",
            context=question_classification
        )

        # Step 5: Format the answer
        answer_formatting = await self.generate(
            instruction=f"""Format the answer according to the expected output:
            Passage: {self.problem_text}
            Operation Result: {operation_execution}
            
            Ensure the answer matches the expected format (number, date, or exact text span).""",
            context=operation_execution
        )

        return answer_formatting