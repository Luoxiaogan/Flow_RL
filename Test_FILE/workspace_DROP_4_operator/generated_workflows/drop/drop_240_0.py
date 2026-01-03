# Workflow ID: drop_240_0
# Benchmark: drop
# Data Indices: [413, 485]

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

        # Step 1: Initial Analysis - Extract entities, numbers, and relationships
        initial_analysis = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - Entities: Names, roles, locations, etc.
            - Numbers: Values and what they represent
            - Relationships: Connections between entities and actions""",
            context=""
        )

        # Step 2: Classify the problem and identify required operations
        problem_classification = await self.generate(
            instruction=f"""Classify the problem based on the question:
            - Is it numerical, logical, or textual?
            - Does it require counting, arithmetic, comparison, or span extraction?
            - What is the expected answer format?
            Passage context: {initial_analysis}""",
            context=initial_analysis
        )

        # Step 3: Generate multiple solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Attempt 1: Solve using direct extraction from the passage.
                Passage context: {initial_analysis}
                Problem type: {problem_classification}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt 2: Solve using arithmetic operations.
                Passage context: {initial_analysis}
                Problem type: {problem_classification}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt 3: Solve using comparison or logical reasoning.
                Passage context: {initial_analysis}
                Problem type: {problem_classification}""",
                context=initial_analysis
            )
        )

        # Step 4: Validate and refine each solution attempt
        refined_attempts = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine the solution attempt. Correct errors and ensure accuracy.",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # Step 5: Ensemble to select the best solution
        final_answer = await self.ensemble(
            instruction="Select the most accurate and complete solution from the refined attempts.",
            contexts_list=refined_attempts
        )

        return final_answer