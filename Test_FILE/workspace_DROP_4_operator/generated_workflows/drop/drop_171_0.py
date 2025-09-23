# Workflow ID: drop_171_0
# Benchmark: drop
# Data Indices: [394, 362]

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
            instruction="""Extract all relevant information from the passage:
            - Named entities (people, places, organizations)
            - Numerical values and their context
            - Relationships between entities
            Format as a structured list with categories.""",
            context=""
        )

        # Step 2: Resolve references in the question
        reference_resolution = await self.generate(
            instruction=f"""Resolve pronouns and partial names in the question:
            - Map 'they', 'the team', etc., to specific entities
            - Ensure alignment with extracted entities: {extraction}
            Provide a mapping of references to entities.""",
            context=extraction
        )

        # Step 3: Classify the question type and required operations
        classification = await self.generate(
            instruction=f"""Classify the question type and required operations:
            - Is it numerical, textual, or comparative?
            - What operations are needed? (e.g., addition, subtraction, span extraction)
            Entities: {extraction}
            Resolved References: {reference_resolution}
            Provide a clear classification and operation plan.""",
            context=f"{extraction}\n{reference_resolution}"
        )

        # Step 4: Execute operations in parallel
        operations = await asyncio.gather(
            self.generate(
                instruction=f"""Execute operation 1: {classification}
                Extract or calculate the required value.""",
                context=f"{extraction}\n{reference_resolution}"
            ),
            self.generate(
                instruction=f"""Execute operation 2: {classification}
                Consider alternative interpretations or methods.""",
                context=f"{extraction}\n{reference_resolution}"
            )
        )

        # Step 5: Ensemble synthesis to select the best result
        synthesis = await self.ensemble(
            instruction=f"""Select the best result from the following options:
            Option 1: {operations[0]}
            Option 2: {operations[1]}
            Criteria: Accuracy, relevance, and format compliance.""",
            contexts_list=operations
        )

        # Step 6: Final refinement and formatting
        final_answer = await self.revise(
            instruction=f"""Refine and format the final answer:
            - Ensure it matches the expected format (number, date, or text span)
            - Remove any ambiguity or redundancy
            Synthesized Result: {synthesis}""",
            context=synthesis
        )

        return final_answer