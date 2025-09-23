# Workflow ID: limr_15_0
# Benchmark: limr
# Data Indices: [255, 117]

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

        # Step 1: Problem Decomposition
        decomposition = await self.generate(
            instruction="""Analyze the problem and break it into sub-problems:
            - Identify key components (e.g., variables, equations, constraints)
            - Suggest intermediate steps required to solve the problem
            - Classify sub-problems by type (algebraic, geometric, combinatorial, etc.)
            - Highlight dependencies between sub-problems""",
            context=""
        )

        # Step 2: Parallel Exploration of Approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Using the decomposition: {decomposition}
                Solve the problem using algebraic methods:
                - Perform all necessary calculations
                - Show intermediate steps
                - Verify results at each stage""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Using the decomposition: {decomposition}
                Solve the problem using geometric methods:
                - Visualize the problem if applicable
                - Use coordinate geometry or vector analysis
                - Validate geometric relationships""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Using the decomposition: {decomposition}
                Solve the problem using combinatorial methods:
                - Count possibilities using permutations or combinations
                - Use generating functions if applicable
                - Verify combinatorial logic""",
                context=decomposition
            )
        )

        # Step 3: Validation and Refinement
        refined_approaches = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the solution:
                - Check all calculations for errors
                - Ensure logical consistency
                - Add missing details or clarifications""",
                context=approach
            ) for approach in approaches]
        )

        # Step 4: Synthesis of Results
        synthesis = await self.ensemble(
            instruction="""Synthesize the refined approaches into a final solution:
            - Evaluate the strengths and weaknesses of each approach
            - Select the most rigorous and elegant solution
            - Ensure all constraints are satisfied""",
            contexts_list=refined_approaches
        )

        # Step 5: Iterative Refinement (Optional)
        final_solution = synthesis
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"""Validate the current solution: {final_solution}
                - Check for errors or inconsistencies
                - Test boundary conditions if applicable
                - Suggest improvements if necessary""",
                context=""
            )
            if "error" not in validation.lower():
                break
            final_solution = await self.revise(
                instruction=f"""Refine the solution based on validation feedback:
                - Address identified issues
                - Improve clarity and precision""",
                context=final_solution
            )

        return final_solution