# Workflow ID: drop_217_0
# Benchmark: drop
# Data Indices: [111, 127]

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
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references in the question
        references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question to specific entities:
            Entities: {entities}
            Question: [QUESTION TEXT]
            Provide resolved references.""",
            context=entities
        )

        # Step 3: Identify the required operation(s)
        operations = await asyncio.gather(
            self.generate(
                instruction="""Classify the question type and identify required operations:
                - Arithmetic: Addition, Subtraction, etc.
                - Counting: How many times, how many different, etc.
                - Comparison: Greater than, less than, etc.
                - Span Extraction: Who did, What was, etc.
                Provide operation type and details.""",
                context=references
            ),
            self.generate(
                instruction="""Generate alternative interpretations of the question:
                - Consider multiple possible operations
                - Provide alternative operation types and details.""",
                context=references
            )
        )

        # Step 4: Select the best operation using ensemble
        selected_operation = await self.ensemble(
            instruction="Select the most appropriate operation based on clarity and relevance.",
            contexts_list=operations
        )

        # Step 5: Execute the selected operation
        result = await self.generate(
            instruction=f"""Execute the selected operation:
            Operation: {selected_operation}
            Entities: {entities}
            References: {references}
            Provide detailed reasoning and final answer.""",
            context=selected_operation
        )

        # Step 6: Format the answer appropriately
        formatted_answer = await self.revise(
            instruction="""Format the answer to match the expected output:
            - Number only
            - Date format
            - Exact text span
            Ensure the answer is clear and concise.""",
            context=result
        )

        return formatted_answer