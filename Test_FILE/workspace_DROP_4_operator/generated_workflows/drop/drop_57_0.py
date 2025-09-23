# Workflow ID: drop_57_0
# Benchmark: drop
# Data Indices: [56, 234]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Identify people, places, teams, and other relevant entities
            - Extract all numerical values and what they represent
            - Note any relationships or actions involving these entities and numbers
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Resolve references
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Given the extracted entities and numbers:
            {entities_and_numbers}
            Map references in the question to specific entities in the passage.
            Provide a mapping of references to entities.""",
            context=entities_and_numbers
        )

        # Step 3: Identify required operations
        operation_identification = await self.generate(
            instruction=f"""Analyze the question to determine the required operation(s):
            Given the resolved references:
            {resolved_references}
            Classify the question type (arithmetic, counting, comparison, span extraction, multi-step)
            Identify keywords that indicate the operation(s) needed.
            Provide a detailed plan for solving the problem.""",
            context=resolved_references
        )

        # Step 4: Execute operations
        # Parallelize independent operations
        operations = operation_identification.split('\n')
        operation_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Execute the following operation:
                {op}
                Use the extracted entities and numbers to perform the calculation or comparison.
                Provide the result of the operation.""",
                context=resolved_references
            ) for op in operations if op.strip()]
        )

        # Step 5: Ensemble results
        final_answer = await self.ensemble(
            instruction="""Synthesize the results of all operations into a final answer:
            Combine the results of individual operations to form a complete solution.
            Ensure the answer matches the expected format (number, date, or text span).""",
            contexts_list=operation_results
        )

        # Step 6: Refine and format the final answer
        refined_answer = await self.revise(
            instruction="""Refine and format the final answer:
            Ensure the answer is clear, accurate, and matches the expected format.
            Correct any errors or ambiguities.""",
            context=final_answer
        )

        return refined_answer