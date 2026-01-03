# Workflow ID: drop_73_0
# Benchmark: drop
# Data Indices: [421, 3]

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
        extraction = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage. 
            - Entities: People, places, organizations, etc.
            - Numbers: All numerical values and their context
            - Relationships: Connections between entities and actions
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify the problem type and required operations
        classification = await self.generate(
            instruction=f"""Analyze the question and classify the problem:
            - Is it numerical, logical, or textual?
            - What operations are required? (e.g., addition, subtraction, comparison)
            - What is the expected answer format? (number, date, text span)
            Context: {extraction}""",
            context=extraction
        )

        # Step 3: Resolve references (pronouns, partial names)
        resolved_references = await self.revise(
            instruction="""Resolve all pronouns and partial names to specific entities:
            - Replace 'he', 'she', 'it', etc., with full names or clear references
            - Ensure all entities are explicitly identified""",
            context=extraction
        )

        # Step 4: Perform operations (parallelize if multiple operations are needed)
        operations = classification.lower().split("operations:")
        if "addition" in operations or "subtraction" in operations:
            # Example: Parallelize arithmetic operations
            operation_results = await asyncio.gather(
                self.generate(
                    instruction="Perform addition operations based on extracted numbers.",
                    context=resolved_references
                ),
                self.generate(
                    instruction="Perform subtraction operations based on extracted numbers.",
                    context=resolved_references
                )
            )
            combined_operations = "\n".join(operation_results)
        else:
            combined_operations = resolved_references

        # Step 5: Validate and format the answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the results into a final answer:
            - Ensure the answer matches the expected format
            - Validate against the question and passage
            - Provide the most accurate and concise response""",
            contexts_list=[resolved_references, combined_operations]
        )

        return final_answer