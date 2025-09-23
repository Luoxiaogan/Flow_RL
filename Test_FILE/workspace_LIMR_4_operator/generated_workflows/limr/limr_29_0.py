# Workflow ID: limr_29_0
# Benchmark: limr
# Data Indices: [134, 40]

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
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and identify key components:
            - Classify the problem type (geometry, number theory, algebra, etc.)
            - Extract all variables, constants, and relationships
            - List all constraints and conditions
            - Identify what needs to be solved or proven""",
            context=""
        )

        # Step 2: Parallel Solution Paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic manipulation:
                - Focus on equations, formulas, and symbolic reasoning
                - Show all steps and maintain precision
                {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using combinatorial reasoning:
                - Apply counting principles, probability, and permutations
                - Consider all possible cases systematically
                {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using geometric interpretation:
                - Use coordinate geometry, trigonometry, and vector calculations
                - Visualize the problem and identify symmetries
                {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Step 3: Iterative Refinement
        refined_solutions = []
        for path in solution_paths:
            refined = await self.revise(
                instruction="""Validate and refine the solution:
                - Check for logical consistency and correctness
                - Correct any errors or gaps in reasoning
                - Improve clarity and presentation""",
                context=path
            )
            refined_solutions.append(refined)

        # Step 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="""Evaluate and synthesize the refined solutions:
            - Select the most complete and correct solution
            - Combine complementary insights if necessary
            - Ensure the final answer is an integer between 000 and 999""",
            contexts_list=refined_solutions
        )

        return final_solution