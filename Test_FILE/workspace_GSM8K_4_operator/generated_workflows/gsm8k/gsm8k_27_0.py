# Workflow ID: gsm8k_27_0
# Benchmark: gsm8k
# Data Indices: [169, 57]

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
        import re

        # Step 1: Extract key information
        extraction = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships:
            - Identify numbers and their context (e.g., units, descriptions)
            - List entities (people, objects) and their roles
            - Highlight relationships and operations mentioned""",
            context=""
        )

        # Step 2: Identify the question and required operations
        question_analysis = await self.generate(
            instruction=f"""Based on the extracted information:
            {extraction}
            
            Identify the question being asked and the required operations:
            - What is the goal (e.g., total, difference, ratio)?
            - What sequence of operations is needed?""",
            context=extraction
        )

        # Step 3: Generate multiple solution attempts
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct computation:
                {question_analysis}""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Solve using step-by-step reasoning:
                {question_analysis}""",
                context=extraction
            )
        )

        # Step 4: Validate and refine solutions
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Validate calculations and improve clarity",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 5: Select the best solution
        final_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution",
            contexts_list=refined_solutions
        )

        # Step 6: Extract and return the final numerical answer
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from:
            {final_solution}
            
            Ensure it is numerically exact and formatted correctly.""",
            context=final_solution
        )

        # Clean up and return the result
        match = re.search(r'\d+(\.\d+)?', final_answer)
        return float(match.group()) if match else None