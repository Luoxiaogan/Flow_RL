# Workflow ID: drop_209_0
# Benchmark: drop
# Data Indices: [4, 320]

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

        # Step 1: Extract key information from the passage
        extraction = await self.generate(
            instruction="""Extract all entities, numbers, relationships, and constraints from the passage.
            Format as a structured list with categories:
            - Entities: [names, roles, locations]
            - Numbers: [values and what they represent]
            - Relationships: [connections between entities]
            - Constraints: [conditions or limitations]""",
            context=""
        )

        # Step 2: Analyze the question to identify required operations
        analysis = await self.generate(
            instruction=f"""Analyze the question to determine the required operations.
            Given the extracted information: {extraction}
            Identify:
            - What entities or numbers are relevant?
            - What operations are needed? (e.g., addition, subtraction, comparison)
            - What is the expected answer format? (e.g., number, text span)""",
            context=extraction
        )

        # Step 3: Generate multiple solution attempts in parallel
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using a direct approach.
                Relevant information: {extraction}
                Analysis: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using an indirect approach.
                Relevant information: {extraction}
                Analysis: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using a step-by-step breakdown.
                Relevant information: {extraction}
                Analysis: {analysis}""",
                context=analysis
            )
        )

        # Step 4: Validate and refine solutions
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Improve clarity and ensure correctness.",
                context=solution
            ) for solution in solutions]
        )

        # Step 5: Synthesize the best solution
        final_answer = await self.ensemble(
            instruction="""Compare the solutions and select the most accurate and complete one.
            Ensure the answer matches the expected format.""",
            contexts_list=refined_solutions
        )

        return final_answer