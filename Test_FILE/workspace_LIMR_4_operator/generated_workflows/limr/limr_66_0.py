# Workflow ID: limr_66_0
# Benchmark: limr
# Data Indices: [191, 185]

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

        # Step 1: Initial Analysis - Identify problem type and key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify its mathematical domain (e.g., geometry, number theory).
            - Extract key variables, equations, or relationships.
            - Determine the expected answer format (integer between 000 and 999).
            - Highlight any constraints or special conditions.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition - Break down into sub-problems
        decomposition = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Decompose the problem into smaller, solvable sub-problems:
            - Define each sub-problem clearly.
            - Specify dependencies between them.
            - Suggest potential solution strategies for each.""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration - Generate multiple solution attempts
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic manipulation:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using geometric reasoning:
                {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using combinatorial methods:
                {decomposition}""",
                context=decomposition
            )
        )

        # Step 4: Validation - Check intermediate results for correctness
        validations = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the solution attempt:
                - Check calculations for errors.
                - Ensure logical consistency.
                - Verify adherence to constraints.""",
                context=attempt
            ) for attempt in solution_attempts]
        )

        # Step 5: Ensemble Evaluation - Select the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate all validated solutions:
            - Compare their correctness and completeness.
            - Choose the most rigorous and precise solution.
            - Ensure the final answer is an integer between 000 and 999.""",
            contexts_list=validations
        )

        # Step 6: Iterative Refinement - Improve the selected solution
        refined_solution = await self.revise(
            instruction="""Refine the final solution:
            - Add missing details or clarifications.
            - Double-check all steps and calculations.
            - Present the answer in the required format.""",
            context=final_solution
        )

        return refined_solution