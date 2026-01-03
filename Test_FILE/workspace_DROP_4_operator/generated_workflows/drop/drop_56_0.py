# Workflow ID: drop_56_0
# Benchmark: drop
# Data Indices: [136, 78]

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

        # Step 1: Initial Problem Analysis
        problem_analysis = await self.generate(
            instruction="""Classify the problem type and identify key components:
            - Is it arithmetic, counting, comparison, or span extraction?
            - What entities, numbers, or relationships are mentioned in the question?
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Parallel Information Extraction
        entities_task = self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People/Teams: [names and roles]
            - Numbers: [values and what they represent]
            - Events: [what happens and when]""",
            context=""
        )
        references_task = self.generate(
            instruction=f"""Resolve references in the question:
            - Match pronouns and partial names to specific entities in the passage.
            - Provide a mapping of references to entities.""",
            context=problem_analysis
        )
        entities, references = await asyncio.gather(entities_task, references_task)

        # Step 3: Conditional Branching Based on Problem Type
        if "arithmetic" in problem_analysis.lower():
            result = await self.solve_arithmetic(entities, references)
        elif "counting" in problem_analysis.lower():
            result = await self.solve_counting(entities, references)
        elif "comparison" in problem_analysis.lower():
            result = await self.solve_comparison(entities, references)
        elif "span extraction" in problem_analysis.lower():
            result = await self.solve_span_extraction(entities, references)
        else:
            result = await self.generate(
                instruction="Apply general problem-solving framework...",
                context=f"{entities}\n{references}"
            )

        # Step 4: Final Answer Formatting and Validation
        final_answer = await self.revise(
            instruction="Format the answer to match the expected output and validate correctness.",
            context=result
        )

        return final_answer

    async def solve_arithmetic(self, entities, references):
        return await self.generate(
            instruction=f"""Perform arithmetic operations:
            - Identify relevant numbers from: {entities}
            - Execute the required operation (addition, subtraction, etc.)
            - Validate intermediate results.""",
            context=references
        )

    async def solve_counting(self, entities, references):
        return await self.generate(
            instruction=f"""Count occurrences of specific events or entities:
            - Identify target events/entities from: {entities}
            - Count their occurrences in the passage.
            - Validate the count.""",
            context=references
        )

    async def solve_comparison(self, entities, references):
        return await self.generate(
            instruction=f"""Compare two or more values or entities:
            - Identify values/entities to compare from: {entities}
            - Determine the relationship (greater than, less than, equal to).
            - Validate the comparison.""",
            context=references
        )

    async def solve_span_extraction(self, entities, references):
        return await self.generate(
            instruction=f"""Extract exact text spans:
            - Identify the relevant part of the passage from: {entities}
            - Ensure the span matches the question's context.
            - Validate the extraction.""",
            context=references
        )