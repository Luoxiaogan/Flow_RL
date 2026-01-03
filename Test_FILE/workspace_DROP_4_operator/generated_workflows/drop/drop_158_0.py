# Workflow ID: drop_158_0
# Benchmark: drop
# Data Indices: [299, 494]

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
            - Named entities (people, teams, locations)
            - Numbers and their contexts (e.g., '1-yard TD pass')
            - Events and actions described in chronological order
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Analyze the question and classify the required operation
        question_analysis = await self.generate(
            instruction=f"""Analyze the question and classify the required operation(s):
            Passage Context: {extraction}
            Identify whether the question requires counting, addition, subtraction, comparison, span extraction, or multi-step reasoning.
            Provide a clear mapping of the operation to the relevant parts of the passage.""",
            context=extraction
        )

        # Step 3: Explore solution paths in parallel
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using the first interpretation:
                Passage Context: {extraction}
                Operation: {question_analysis}""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Solve the problem using an alternative interpretation:
                Passage Context: {extraction}
                Operation: {question_analysis}""",
                context=extraction
            )
        )

        # Step 4: Validate and revise each path
        revised_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and improve the answer:
                Ensure the format matches the expected output (number, date, or exact text span).
                Correct any errors or inconsistencies.""",
                context=path
            ) for path in paths]
        )

        # Step 5: Select the best answer using ensemble
        final_answer = await self.ensemble(
            instruction="""Select the best answer:
            Criteria:
            - Consistency with the passage
            - Clarity and correctness
            - Adherence to the question's requirements""",
            contexts_list=revised_paths
        )

        return final_answer