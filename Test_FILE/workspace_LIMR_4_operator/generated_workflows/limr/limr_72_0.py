# Workflow ID: limr_72_0
# Benchmark: limr
# Data Indices: [56, 11]

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
            instruction="""Analyze the problem structure:
            - Identify key components (equations, constraints, figures)
            - Classify the problem type (algebraic, geometric, combinatorial, etc.)
            - Extract variables, constants, and relationships
            - Highlight any special conditions or constraints
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop an algebraic solution approach:
                - Use equations and variables from: {decomposition}
                - Apply algebraic manipulation and transformations
                - Solve step-by-step with full precision""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Develop a geometric solution approach:
                - Use figures and spatial relationships from: {decomposition}
                - Apply coordinate geometry, vectors, or trigonometry
                - Solve step-by-step with full precision""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Develop a combinatorial solution approach:
                - Use counting principles and constraints from: {decomposition}
                - Apply permutations, combinations, or probability
                - Solve step-by-step with full precision""",
                context=decomposition
            )
        )

        # Step 3: Iterative Refinement
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction=f"""Refine the solution:
                - Check for logical consistency and completeness
                - Verify calculations and algebraic steps
                - Address any gaps or ambiguities
                Current solution: {strategy}""",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Validation Loop
        final_solutions = []
        for refined in refined_strategies:
            valid = False
            for _ in range(3):  # Allow up to 3 refinement iterations
                validation = await self.generate(
                    instruction=f"""Validate the solution:
                    - Ensure all steps are logically sound
                    - Confirm the final answer is an exact integer
                    - Highlight any remaining issues
                    Current solution: {refined}""",
                    context=refined
                )
                if "error" not in validation.lower():
                    valid = True
                    break
                refined = await self.revise(
                    instruction=f"""Fix identified issues:
                    - Address validation feedback: {validation}
                    - Improve clarity and precision
                    Current solution: {refined}""",
                    context=refined
                )
            if valid:
                final_solutions.append(refined)

        # Step 5: Final Synthesis
        final_solution = await self.ensemble(
            instruction=f"""Synthesize the best solution:
            - Select the most rigorous and elegant approach
            - Combine complementary insights from multiple strategies
            - Ensure the final answer is an exact integer between 000 and 999
            Candidate solutions: {final_solutions}""",
            contexts_list=final_solutions
        )

        return final_solution