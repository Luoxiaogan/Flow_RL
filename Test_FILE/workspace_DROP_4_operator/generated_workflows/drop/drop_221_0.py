# Workflow ID: drop_221_0
# Benchmark: drop
# Data Indices: [44, 148]

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
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as structured list.""",
            context=""
        )

        # Step 2: Identify question type and required operations
        analysis = await self.generate(
            instruction="""Classify the problem:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - What operations are needed? (e.g., addition, subtraction, comparison)
            Provide structured classification.""",
            context=entities
        )

        # Step 3: Fork into parallel branches for different perspectives
        entity_resolution, operation_identification, constraints = await asyncio.gather(
            self.generate(
                instruction=f"""Resolve references in the question using entities:
                {entities}
                Map pronouns and partial names to specific entities.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Identify the exact operation(s) required:
                {analysis}
                Provide step-by-step reasoning.""",
                context=entities
            ),
            self.generate(
                instruction=f"""Identify all constraints and conditions:
                {entities}
                Include explicit and implicit constraints.""",
                context=entities
            )
        )

        # Step 4: Process each branch independently
        refined_entity_resolution = await self.revise(
            instruction="Resolve any remaining ambiguities.",
            context=entity_resolution
        )
        refined_operation_identification = await self.revise(
            instruction="Clarify and validate the identified operations.",
            context=operation_identification
        )
        refined_constraints = await self.revise(
            instruction="Refine and expand the list of constraints.",
            context=constraints
        )

        # Step 5: Merge insights using ensemble
        synthesis = await self.ensemble(
            instruction="""Synthesize all perspectives into a unified solution:
            - Use resolved entities to interpret the question.
            - Apply identified operations within the constraints.
            - Ensure the answer matches the expected format.""",
            contexts_list=[refined_entity_resolution, refined_operation_identification, refined_constraints]
        )

        # Step 6: Validate and finalize the answer
        final_answer = await self.revise(
            instruction="Ensure the answer is correct, complete, and matches the expected format.",
            context=synthesis
        )

        return final_answer