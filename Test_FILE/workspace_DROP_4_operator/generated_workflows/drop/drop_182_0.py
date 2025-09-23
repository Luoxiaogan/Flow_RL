# Workflow ID: drop_182_0
# Benchmark: drop
# Data Indices: [448, 227]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: People, places, organizations, etc.
            - Numbers: Quantities, dates, measurements, etc.
            - Relationships: Actions, events, and connections between entities.
            Format as a structured list.""",
            context=""
        )

        # Step 2: Classify question type and identify required operations
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and classify its type:
            - Is it arithmetic (addition, subtraction, etc.)?
            - Is it counting (how many times, how many different)?
            - Is it comparison (greater, longer, earlier)?
            - Is it span extraction (who, what, when)?
            Also, identify the required operations and entities involved.
            
            Passage Entities: {entities}""",
            context=""
        )

        # Step 3: Generate candidate solutions using parallel forks
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem assuming it's arithmetic:
                - Perform necessary calculations (addition, subtraction, etc.).
                - Ensure all relevant numbers are used.
                
                Question Analysis: {question_analysis}
                Passage Entities: {entities}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it's counting:
                - Count occurrences of specific events or entities.
                - Ensure no instances are missed.
                
                Question Analysis: {question_analysis}
                Passage Entities: {entities}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it's comparison:
                - Compare magnitudes, sequences, or other attributes.
                - Clearly state which is greater/longer/earlier.
                
                Question Analysis: {question_analysis}
                Passage Entities: {entities}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it's span extraction:
                - Extract exact text spans matching the question.
                - Ensure the span matches the passage exactly.
                
                Question Analysis: {question_analysis}
                Passage Entities: {entities}""",
                context=""
            )
        )

        # Step 4: Validate and refine results through iterative revision
        refined_candidates = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine this solution:
                - Correct any errors or omissions.
                - Ensure the answer matches the expected format.
                
                Candidate Solution: {candidate}""",
                context=candidate
            ) for candidate in candidates]
        )

        # Step 5: Use Ensemble to select the best solution
        final_answer = await self.ensemble(
            instruction="""Select the best solution:
            - Ensure it answers the question correctly.
            - Verify the format matches expectations.
            - Choose the most plausible option if multiple are valid.""",
            contexts_list=refined_candidates
        )

        return final_answer