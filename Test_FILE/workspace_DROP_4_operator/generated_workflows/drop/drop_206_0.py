# Workflow ID: drop_206_0
# Benchmark: drop
# Data Indices: [159, 454]

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

        # Step 1: Extract all relevant entities and numbers
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Resolve references and clarify ambiguities
        resolved_references = await self.revise(
            instruction=f"""Resolve all pronouns and partial names to specific entities:
            Original Entities: {entities}
            Ensure each reference is clear and unambiguous.""",
            context=entities
        )

        # Step 3: Generate multiple interpretations of the problem
        interpretations = await asyncio.gather(
            self.generate(
                instruction=f"""Interpret the problem as an arithmetic task:
                Operations: Addition, Subtraction, Counting
                Context: {resolved_references}""",
                context=""
            ),
            self.generate(
                instruction=f"""Interpret the problem as a comparison task:
                Operations: Greater/Less Than, Earliest/Latest
                Context: {resolved_references}""",
                context=""
            ),
            self.generate(
                instruction=f"""Interpret the problem as a span extraction task:
                Operations: Exact text matching
                Context: {resolved_references}""",
                context=""
            )
        )

        # Step 4: Process each interpretation independently
        processed_interpretations = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the interpretation:
                Original Interpretation: {interp}
                Ensure logical consistency and completeness.""",
                context=interp
            ) for interp in interpretations]
        )

        # Step 5: Summarize each processed interpretation
        summarized_interpretations = await asyncio.gather(
            *[self.summarize(
                instruction=f"""Condense the interpretation while preserving key points:
                Original Interpretation: {proc_interp}""",
                context=proc_interp
            ) for proc_interp in processed_interpretations]
        )

        # Step 6: Ensemble to select the best solution
        final_answer = await self.ensemble(
            instruction="""Select the best solution based on:
            - Logical consistency with the passage
            - Match with expected answer format
            - Completeness of reasoning""",
            contexts_list=summarized_interpretations
        )

        return final_answer