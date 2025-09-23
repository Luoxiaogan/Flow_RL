# Workflow ID: limr_17_0
# Benchmark: limr
# Data Indices: [86, 49]

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
            instruction="""Analyze the problem structure:
            - Identify the problem type (e.g., algebra, geometry, number theory).
            - Extract key components and constraints.
            - Highlight any special conditions or requirements.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Sub-Problem Generation
        sub_problems = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Break the problem into sub-problems:
            - Define each sub-problem clearly.
            - Specify objectives and constraints.
            - Suggest potential solution strategies.""",
            context=analysis
        )

        # Step 3: Parallel Solution Exploration
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                Sub-problems: {sub_problems}
                Show all steps and maintain precision.""",
                context=sub_problems
            ),
            self.generate(
                instruction=f"""Solve using geometric methods:
                Sub-problems: {sub_problems}
                Use visual reasoning where applicable.""",
                context=sub_problems
            ),
            self.generate(
                instruction=f"""Solve using combinatorial methods:
                Sub-problems: {sub_problems}
                Focus on counting principles and probability.""",
                context=sub_problems
            )
        )

        # Step 4: Validation and Refinement
        refined_solutions = []
        for solution in solutions:
            validated = await self.revise(
                instruction="""Validate the solution:
                - Check all steps for correctness.
                - Ensure constraints are satisfied.
                - Verify the final answer format.""",
                context=solution
            )
            refined = await self.revise(
                instruction="Refine the solution based on validation feedback.",
                context=validated
            )
            refined_solutions.append(refined)

        # Step 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Compare results from different methods.
            - Select the most precise and well-supported answer.
            - Ensure the final answer is an integer between 000 and 999.""",
            contexts_list=refined_solutions
        )

        # Step 6: Final Verification
        verified_solution = await self.revise(
            instruction="""Perform final verification:
            - Double-check calculations.
            - Confirm the answer satisfies all constraints.
            - Format the answer as a three-digit integer.""",
            context=final_solution
        )

        return verified_solution