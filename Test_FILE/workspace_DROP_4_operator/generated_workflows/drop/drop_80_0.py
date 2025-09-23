# Workflow ID: drop_80_0
# Benchmark: drop
# Data Indices: [429, 55]

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
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references
        references = await self.generate(
            instruction=f"""Resolve pronouns and partial names to specific entities:
            Passage: {self.problem_text}
            Extracted Entities: {entities}""",
            context=entities
        )

        # Step 3: Identify required operations
        operations = await self.generate(
            instruction=f"""Analyze the question and determine the required operation(s):
            Question: {self.problem_text.split('QUESTION:')[1].split('ANSWER:')[0].strip()}
            Extracted Entities: {entities}
            Resolved References: {references}""",
            context=f"{entities}\n{references}"
        )

        # Step 4: Execute operations
        execution_results = await asyncio.gather(
            self.generate(
                instruction=f"""Perform the identified operations:
                Operations: {operations}
                Extracted Entities: {entities}
                Resolved References: {references}""",
                context=f"{entities}\n{references}\n{operations}"
            ),
            self.generate(
                instruction=f"""Cross-validate the operations:
                Operations: {operations}
                Extracted Entities: {entities}
                Resolved References: {references}""",
                context=f"{entities}\n{references}\n{operations}"
            )
        )

        # Step 5: Validate and refine
        final_result = await self.ensemble(
            instruction="""Synthesize the results and ensure accuracy:
            - Compare outputs for consistency
            - Resolve discrepancies
            - Format the final answer appropriately""",
            contexts_list=execution_results
        )

        return final_result