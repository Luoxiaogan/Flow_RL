# Workflow ID: limr_101_0
# Benchmark: limr
# Data Indices: [196, 76]

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

        # Phase 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem to classify its domain and extract key components:
            - Identify the main mathematical domain (geometry, number theory, combinatorics, etc.)
            - Extract all variables, constants, and relationships
            - List explicit and implicit constraints
            - Highlight any special cases or edge conditions""",
            context=""
        )

        # Phase 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop an algebraic/analytical solution approach:
                - Use symbolic manipulation and equations
                - Focus on precision and exact calculations
                Context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a geometric/visual solution approach:
                - Use diagrams, coordinate transformations, or trigonometric identities
                - Focus on spatial reasoning and symmetry
                Context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a combinatorial/probabilistic solution approach:
                - Use counting principles, permutations, or probability distributions
                - Focus on enumeration and logical reasoning
                Context: {analysis}""",
                context=analysis
            )
        )

        # Phase 3: Ensemble Selection and Refinement
        selected_strategy = await self.ensemble(
            instruction="""Evaluate the candidate strategies:
            - Choose the most rigorous and clear approach
            - Ensure alignment with problem constraints and requirements
            - Prioritize solutions that address edge cases effectively""",
            contexts_list=strategies
        )

        refined_solution = await self.revise(
            instruction="""Refine the selected solution:
            - Verify all calculations and logical steps
            - Add missing details or clarify ambiguous points
            - Ensure the final answer is an integer between 000 and 999""",
            context=selected_strategy
        )

        # Phase 4: Iterative Refinement (if needed)
        validation = await self.generate(
            instruction=f"""Validate the refined solution:
            - Check for errors or inconsistencies
            - Confirm alignment with problem requirements
            Context: {refined_solution}""",
            context=refined_solution
        )

        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Address identified issues:
                - Fix errors or inconsistencies
                - Revalidate the solution""",
                context=refined_solution
            )

        return refined_solution