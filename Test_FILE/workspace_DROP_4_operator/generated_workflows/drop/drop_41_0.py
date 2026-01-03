# Workflow ID: drop_41_0
# Benchmark: drop
# Data Indices: [52, 233]

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
            instruction="""Extract all named entities, numbers, and relationships from the passage.
            Format as a structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Question Classification - Identify the problem type and required operation
        classification = await self.generate(
            instruction=f"""Classify the question based on the extracted information:
            {initial_analysis}
            
            Determine:
            - Is it numerical, textual, or comparative?
            - What operation is required? (e.g., addition, subtraction, counting, comparison)
            - What is the expected answer format? (e.g., number, date, text span)""",
            context=initial_analysis
        )

        # Step 3: Parallel Solution Attempts
        # Generate multiple solution attempts using different strategies
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using direct extraction:
                {classification}
                
                Focus on extracting exact matches from the passage.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using arithmetic computation:
                {classification}
                
                Perform any required calculations based on the extracted numbers.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using comparison:
                {classification}
                
                Compare values or entities as required by the question.""",
                context=initial_analysis
            )
        )

        # Step 4: Validation and Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine this solution:
                {solution}
                
                Ensure it matches the question requirements and passage content.""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 5: Synthesis - Select the best solution or synthesize multiple solutions
        final_answer = await self.ensemble(
            instruction=f"""Select the best solution or synthesize multiple solutions:
            {classification}
            
            Criteria:
            - Accuracy: Does it match the question requirements?
            - Completeness: Does it address all parts of the question?
            - Precision: Is it formatted correctly?""",
            contexts_list=refined_solutions
        )

        return final_answer