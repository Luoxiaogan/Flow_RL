# Workflow ID: drop_6_0
# Benchmark: drop
# Data Indices: [135, 53]

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
        entities = await self.generate(
            instruction="""Extract all named entities, numbers, and relationships:
            Format as structured list with categories:
            - People: [names and roles]
            - Places: [locations and contexts]
            - Numbers: [values and what they represent]
            - Actions: [what happens and when]""",
            context=""
        )

        # Step 2: Problem Classification - Identify question type and required operations
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted entities:
            Entities: {entities}
            
            Determine:
            - Is it numerical, logical, or textual?
            - Does it require exact calculation or estimation?
            - What operations are needed (addition, subtraction, counting, comparison)?
            - What is the expected answer format?""",
            context=entities
        )

        # Step 3: Parallel Solution Generation - Generate multiple solution attempts
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using arithmetic operations:
                Entities: {entities}
                Classification: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using counting logic:
                Entities: {entities}
                Classification: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using comparison logic:
                Entities: {entities}
                Classification: {classification}""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using span extraction:
                Entities: {entities}
                Classification: {classification}""",
                context=""
            )
        )

        # Step 4: Validation and Refinement - Refine each solution attempt
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution: {solution}",
                context=solution
            ) for solution in solutions]
        )

        # Step 5: Ensemble Synthesis - Select the best solution
        final_answer = await self.ensemble(
            instruction="Select the most accurate and complete solution",
            contexts_list=refined_solutions
        )

        return final_answer