# Workflow ID: drop_245_0
# Benchmark: drop
# Data Indices: [438, 61]

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
        import re

        # Step 1: Entity and Number Extraction
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Reference Resolution
        resolved_references = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve pronouns and partial names to specific entities:
                Entities: {entities}
                Ensure consistency and clarity.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Explore alternative interpretations of ambiguous references:
                Entities: {entities}
                Provide multiple possibilities.""",
                context=entities
            )
        )
        references = await self.ensemble(
            instruction="Select the most consistent and complete reference resolution.",
            contexts_list=resolved_references
        )

        # Step 3: Operation Identification
        operation_type = await self.generate(
            instruction=f"""Classify the problem type:
            Entities: {entities}
            References: {references}
            Possible types: arithmetic, counting, comparison, span extraction.
            Provide clear reasoning.""",
            context=f"{entities}

{references}"
        )

        # Step 4: Operation Execution
        if "arithmetic" in operation_type.lower():
            numbers = re.findall(r'\d+', entities)
            result = sum(map(int, numbers))  # Example: Sum all numbers
        elif "counting" in operation_type.lower():
            result = len(re.findall(r'\b\w+\b', entities))  # Example: Count words
        elif "comparison" in operation_type.lower():
            numbers = re.findall(r'\d+', entities)
            result = max(map(int, numbers))  # Example: Find maximum
        else:  # Span extraction
            result = await self.generate(
                instruction=f"""Extract the exact text span answering the question:
                Passage: {self.problem_text}
                Question: {operation_type}""",
                context=""
            )

        # Step 5: Validation and Refinement
        validated_result = await self.revise(
            instruction=f"""Validate and refine the result:
            Expected format: number, date, or exact text span.
            Result: {result}""",
            context=result
        )

        # Step 6: Final Answer Selection
        final_answer = await self.ensemble(
            instruction="Select the most precise and valid answer.",
            contexts_list=[result, validated_result]
        )

        return final_answer