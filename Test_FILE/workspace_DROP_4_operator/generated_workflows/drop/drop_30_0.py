# Workflow ID: drop_30_0
# Benchmark: drop
# Data Indices: [86, 237]

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

        # Step 1: Extract key information from the passage
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Organize as a structured list.""",
            context=""
        )

        # Step 2: Classify the problem type
        classification = await self.generate(
            instruction=f"""Classify this problem based on the question:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - What is the expected answer format (number, date, text span)?
            Passage Entities: {entities}""",
            context=""
        )

        # Step 3: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve all pronouns and partial names in the question:
            - Map pronouns to specific entities in the passage
            - Clarify ambiguous references
            Passage Entities: {entities}
            Question Classification: {classification}""",
            context=classification
        )

        # Step 4: Identify required operations
        operations = await self.generate(
            instruction=f"""Based on the question and resolved references, identify the required operations:
            - Arithmetic (addition, subtraction, counting)
            - Comparison (greater/less than, earliest/latest)
            - Textual extraction (exact span matching)
            Passage Entities: {entities}
            Resolved References: {resolved_references}""",
            context=resolved_references
        )

        # Step 5: Execute operations in parallel
        operation_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform arithmetic operations (addition, subtraction, counting):
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Identified Operations: {operations}""",
                context=operations
            ),
            self.generate(
                instruction=f"""Perform comparison operations (greater/less than, earliest/latest):
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Identified Operations: {operations}""",
                context=operations
            ),
            self.generate(
                instruction=f"""Perform textual extraction (exact span matching):
                Passage Entities: {entities}
                Resolved References: {resolved_references}
                Identified Operations: {operations}""",
                context=operations
            )
        )

        # Step 6: Ensemble to select the best answer
        final_answer = await self.ensemble(
            instruction=f"""Select the best answer from the following options:
            - Ensure the answer matches the expected format (number, date, text span)
            - Verify the answer aligns with the passage
            Passage Entities: {entities}
            Operation Results: {operation_results}""",
            contexts_list=operation_results
        )

        return final_answer