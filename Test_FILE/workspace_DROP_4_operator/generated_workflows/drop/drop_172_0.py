# Workflow ID: drop_172_0
# Benchmark: drop
# Data Indices: [434, 221]

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

        # Step 1: Extract key information from the passage
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Analyze the question to classify its type and requirements
        analysis = await self.generate(
            instruction="""Analyze the question:
            - What type of operation is required? (arithmetic, counting, comparison, span extraction)
            - What references need to be resolved?
            - What is the expected answer format?""",
            context=entities
        )

        # Step 3: Resolve references in the question
        resolved_references = await self.generate(
            instruction=f"""Resolve question references to specific entities in the passage:
            Entities: {entities}
            Question: [QUESTION TEXT]
            Provide explicit mappings for pronouns, partial names, or ambiguous terms.""",
            context=analysis
        )

        # Step 4: Identify candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Find all relevant instances for the required operation:
                Operation: [OPERATION TYPE]
                Context: {resolved_references}""",
                context=entities
            ),
            self.generate(
                instruction=f"""Validate and refine the extracted information:
                Ensure all candidates are accurate and complete.""",
                context=resolved_references
            )
        )

        # Step 5: Ensemble to select the best answer
        best_answer = await self.ensemble(
            instruction="""Select the best candidate or synthesize multiple options:
            - Ensure the answer matches the expected format.
            - Prioritize clarity and correctness.""",
            contexts_list=candidates
        )

        # Step 6: Validate and refine the final answer
        final_answer = await self.revise(
            instruction="""Verify the answer:
            - Check for formatting compliance.
            - Ensure it addresses the question fully.
            - Correct any errors or ambiguities.""",
            context=best_answer
        )

        return final_answer