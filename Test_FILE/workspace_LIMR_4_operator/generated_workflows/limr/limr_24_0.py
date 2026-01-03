# Workflow ID: limr_24_0
# Benchmark: limr
# Data Indices: [82, 104]

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
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the main mathematical domain (geometry, number theory, etc.)
            - Extract key variables, constraints, and relationships
            - Highlight potential solution strategies
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        sub_problems = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Break the problem into sub-problems:
            - Define each sub-problem clearly
            - Specify dependencies between sub-problems
            - Suggest possible approaches for each""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration of Approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                {sub_problems}""",
                context=sub_problems
            ),
            self.generate(
                instruction=f"""Solve using geometric interpretation:
                {sub_problems}""",
                context=sub_problems
            ),
            self.generate(
                instruction=f"""Solve using combinatorial reasoning:
                {sub_problems}""",
                context=sub_problems
            )
        )

        # Step 4: Synthesize and Select Best Approach
        synthesis = await self.ensemble(
            instruction="""Evaluate the approaches:
            - Assess correctness and completeness
            - Consider computational efficiency
            - Select the most promising solution""",
            contexts_list=approaches
        )

        # Step 5: Iterative Refinement
        refined_solution = synthesis
        for _ in range(3):  # Allow up to 3 refinement cycles
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {refined_solution}
                
                Check for:
                - Logical consistency
                - Calculation accuracy
                - Compliance with problem constraints""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Fix identified issues:
                    {validation}""",
                    context=refined_solution
                )
            else:
                break

        # Step 6: Final Answer Extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final answer from the refined solution:
            {refined_solution}
            
            Ensure the answer is an integer between 000 and 999.""",
            context=refined_solution
        )

        return final_answer