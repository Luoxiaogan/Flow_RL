# Workflow ID: drop_102_0
# Benchmark: drop
# Data Indices: [330, 181]

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
            instruction="""Extract all relevant entities, numbers, and relationships from the passage:
            - Entities: Names, places, teams, etc.
            - Numbers: All numerical values and their context
            - Relationships: How entities and numbers relate to each other
            Then analyze the question to determine the required operation(s):
            - Arithmetic: Addition, subtraction, etc.
            - Counting: How many times something occurs
            - Comparison: Which is greater, longer, etc.
            Provide structured output.""",
            context=""
        )

        # Step 2: Refine and validate extraction
        refined_extraction = await self.revise(
            instruction="""Review the extracted information and proposed operations:
            - Verify entity mappings are correct
            - Ensure all relevant numbers are included
            - Check operation identification matches question phrasing
            - Correct any errors and improve clarity""",
            context=extraction
        )

        # Step 3: Summarize key information
        summary = await self.summarize(
            instruction="""Condense the extracted information into a concise summary:
            - Include only key entities, numbers, and relationships
            - Focus on information directly relevant to the question
            - Maintain clarity and logical flow""",
            context=refined_extraction
        )

        # Step 4: Generate multiple solution attempts in parallel
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"Using the summary: {summary}, solve using arithmetic operations.",
                context=summary
            ),
            self.generate(
                instruction=f"Using the summary: {summary}, solve using counting operations.",
                context=summary
            ),
            self.generate(
                instruction=f"Using the summary: {summary}, solve using comparison operations.",
                context=summary
            )
        )

        # Step 5: Ensemble to select the best solution
        final_answer = await self.ensemble(
            instruction="""Evaluate the solution attempts:
            - Check for correctness and completeness
            - Validate against expected answer format
            - Select the most accurate and well-supported solution""",
            contexts_list=solutions
        )

        return final_answer