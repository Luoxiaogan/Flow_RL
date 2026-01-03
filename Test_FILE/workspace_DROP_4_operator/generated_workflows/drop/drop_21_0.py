# Workflow ID: drop_21_0
# Benchmark: drop
# Data Indices: [213, 134]

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

        # Phase 1: Entity and Relationship Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        references = await self.generate(
            instruction=f"""Resolve references in the question to specific entities in the passage.
            Passage Entities: {entities}
            Question: {{QUESTION}}
            Identify which entities the question refers to.""",
            context=entities
        )

        # Phase 2: Operation Classification
        classification = await self.generate(
            instruction=f"""Classify the question into one of the following categories:
            1. Arithmetic (e.g., addition, subtraction)
            2. Counting (e.g., how many times, how many different)
            3. Comparison (e.g., which is greater, who had more)
            4. Span Extraction (e.g., who did, what was the name of)
            5. Multi-step (requires chaining multiple operations)
            
            Passage Entities: {entities}
            Resolved References: {references}
            Question: {{QUESTION}}
            Provide the category and reasoning.""",
            context=f"{entities}\n{references}"
        )

        # Phase 3: Operation Execution
        if "arithmetic" in classification.lower():
            result = await self.generate(
                instruction=f"""Perform the required arithmetic operation.
                Passage Entities: {entities}
                Resolved References: {references}
                Question: {{QUESTION}}
                Show all steps and present the final answer as a number.""",
                context=f"{entities}\n{references}\n{classification}"
            )
        elif "counting" in classification.lower():
            result = await self.generate(
                instruction=f"""Count the relevant instances.
                Passage Entities: {entities}
                Resolved References: {references}
                Question: {{QUESTION}}
                Ensure no instances are missed and present the count as a number.""",
                context=f"{entities}\n{references}\n{classification}"
            )
        elif "comparison" in classification.lower():
            result = await self.generate(
                instruction=f"""Compare the specified values.
                Passage Entities: {entities}
                Resolved References: {references}
                Question: {{QUESTION}}
                Clearly state which is greater/longer/more and provide the reasoning.""",
                context=f"{entities}\n{references}\n{classification}"
            )
        elif "span extraction" in classification.lower():
            result = await self.generate(
                instruction=f"""Extract the exact text span that answers the question.
                Passage Entities: {entities}
                Resolved References: {references}
                Question: {{QUESTION}}
                Ensure the span matches the passage exactly.""",
                context=f"{entities}\n{references}\n{classification}"
            )
        else:  # Multi-step
            steps = await self.generate(
                instruction=f"""Identify the sequence of operations required.
                Passage Entities: {entities}
                Resolved References: {references}
                Question: {{QUESTION}}
                List the steps in order.""",
                context=f"{entities}\n{references}\n{classification}"
            )
            result = await self.generate(
                instruction=f"""Execute the identified steps.
                Steps: {steps}
                Passage Entities: {entities}
                Resolved References: {references}
                Question: {{QUESTION}}
                Show all intermediate results and present the final answer.""",
                context=f"{entities}\n{references}\n{classification}\n{steps}"
            )

        # Phase 4: Answer Synthesis
        validated_result = await self.revise(
            instruction=f"""Validate the result against the question and passage.
            Passage Entities: {entities}
            Resolved References: {references}
            Question: {{QUESTION}}
            Result: {result}
            Correct any errors and ensure the format matches expectations.""",
            context=f"{entities}\n{references}\n{classification}\n{result}"
        )

        return validated_result