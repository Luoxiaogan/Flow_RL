# Workflow ID: limr_5_0
# Benchmark: limr
# Data Indices: [15, 222]

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

        # Step 1: Initial Analysis - Understand the problem structure
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the domain (geometry, algebra, number theory, etc.)
            - Extract key variables, constants, and relationships
            - Determine constraints and boundary conditions
            - Highlight any special properties or symmetries
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Strategy Generation - Explore multiple solution approaches
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Develop an algebraic solution strategy:
                - Define equations or transformations
                - Outline step-by-step reasoning
                - Note required calculations or simplifications""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Develop a geometric solution strategy:
                - Visualize the problem if applicable
                - Use coordinates, vectors, or trigonometric relationships
                - Outline step-by-step reasoning""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Develop a combinatorial or number-theoretic solution strategy:
                - Identify counting principles or modular properties
                - Outline step-by-step reasoning
                - Note required optimizations or constraints""",
                context=initial_analysis
            )
        )

        # Step 3: Parallel Execution - Attempt solutions using generated strategies
        attempted_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"Implement the following strategy: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Revision - Improve and validate attempted solutions
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Review and improve the solution: {solution}",
                context=solution
            ) for solution in attempted_solutions]
        )

        # Step 5: Ensemble - Select or synthesize the best solution
        final_solution = await self.ensemble(
            instruction="Evaluate all solutions and select the most precise and complete one.",
            contexts_list=revised_solutions
        )

        # Step 6: Final Validation - Ensure correctness and extract the answer
        validated_solution = await self.revise(
            instruction=f"Validate the final solution: {final_solution}. Ensure all steps are correct and the answer is an integer between 000 and 999.",
            context=final_solution
        )

        return validated_solution