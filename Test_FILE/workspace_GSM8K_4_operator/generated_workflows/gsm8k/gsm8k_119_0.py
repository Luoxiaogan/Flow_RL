# Workflow ID: gsm8k_119_0
# Benchmark: gsm8k
# Data Indices: [224, 48]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Numerical values and their context
            - Relationships between entities
            - What is being asked for
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Problem Classification
        classification = await self.generate(
            instruction=f"""Classify the problem based on the analysis:
            {analysis}
            
            Categories:
            - Sequential operations
            - Rate problems
            - Distribution
            - Proportions
            - Multi-entity tracking
            
            Identify the category and suggest a solution strategy.""",
            context=analysis
        )

        # Step 3: Solution Construction
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem step-by-step using the identified strategy:
                {classification}
                
                Show all intermediate calculations and track units.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Attempt an alternative solution approach:
                {classification}
                
                Explore a different method if applicable.""",
                context=classification
            )
        )

        # Step 4: Validation and Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the solution:
                Check for logical consistency, unit tracking, and numerical accuracy.
                Correct any errors.""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Step 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the refined attempts:
            Ensure the final answer is numerically exact and matches the problem requirements.""",
            contexts_list=refined_solutions
        )

        # Step 6: Final Answer Extraction
        answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_solution
        )

        return answer.strip()