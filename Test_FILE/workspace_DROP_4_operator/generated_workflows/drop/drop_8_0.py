# Workflow ID: drop_8_0
# Benchmark: drop
# Data Indices: [85, 378]

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
        
        # Step 1: Extract entities and numbers from the passage
        entities_and_numbers = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships from the passage:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]
            Format as a structured list.""",
            context=""
        )
        
        # Step 2: Analyze the question to classify its type and identify references
        question_analysis = await self.generate(
            instruction=f"""Analyze the question:
            - What type of operation is required? (e.g., arithmetic, counting, comparison, span extraction)
            - Identify all references (pronouns, partial names) and map them to entities in the passage.
            Passage Entities and Numbers: {entities_and_numbers}""",
            context=""
        )
        
        # Step 3: Generate multiple solution attempts in parallel
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem assuming it requires arithmetic operations:
                Passage Entities and Numbers: {entities_and_numbers}
                Question Analysis: {question_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it requires counting:
                Passage Entities and Numbers: {entities_and_numbers}
                Question Analysis: {question_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it requires comparison:
                Passage Entities and Numbers: {entities_and_numbers}
                Question Analysis: {question_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve the problem assuming it requires exact span extraction:
                Passage Entities and Numbers: {entities_and_numbers}
                Question Analysis: {question_analysis}""",
                context=""
            )
        )
        
        # Step 4: Validate and refine each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine this solution:
                Ensure it matches the question requirements and passage content.
                Solution: {solution}""",
                context=solution
            ) for solution in solution_attempts]
        )
        
        # Step 5: Select the best solution or synthesize insights
        final_answer = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Choose the most accurate and complete answer.
            - Ensure the answer matches the expected format (number, date, or exact text span).""",
            contexts_list=refined_solutions
        )
        
        return final_answer