# Workflow ID: drop_177_0
# Benchmark: drop
# Data Indices: [338, 216]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as structured data:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Classify question type and identify required operation(s)
        classification = await self.generate(
            instruction="""Classify the question type and identify required operation(s):
            - Is it numerical, logical, or textual?
            - Does it require counting, arithmetic, or comparison?
            - What is the expected answer format?""",
            context=extraction
        )

        # Step 3: Parallel processing
        entity_mapping, operation_execution, validation = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve references in the question to specific entities in the passage:
                Passage Entities: {extraction}
                Question: [Question from problem text]""",
                context=classification
            ),
            self.generate(
                instruction=f"""Perform the required operation(s) using the extracted data:
                Extracted Data: {extraction}
                Required Operation: [Operation from classification]""",
                context=classification
            ),
            self.generate(
                instruction=f"""Validate intermediate results:
                Extracted Data: {extraction}
                Operation Results: [Results from operation_execution]""",
                context=classification
            )
        )

        # Step 4: Synthesize results
        synthesis = await self.ensemble(
            instruction="""Combine the results of entity mapping, operation execution, and validation into a unified solution.
            Ensure the final answer matches the expected format.""",
            contexts_list=[entity_mapping, operation_execution, validation]
        )

        # Step 5: Revise and finalize answer
        final_answer = await self.revise(
            instruction="Ensure the answer is in the correct format and matches the expected output.",
            context=synthesis
        )

        return final_answer