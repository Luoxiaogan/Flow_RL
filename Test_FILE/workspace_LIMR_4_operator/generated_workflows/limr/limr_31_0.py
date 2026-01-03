# Workflow ID: limr_31_0
# Benchmark: limr
# Data Indices: [36, 171]

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
            - Classify the problem type (e.g., algebraic, geometric, combinatorial).
            - Identify key components (variables, constraints, relationships).
            - Highlight any special cases or edge conditions.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop an algebraic solution strategy based on:
                {analysis}
                Focus on polynomial equations, functional equations, or inequalities.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a combinatorial solution strategy based on:
                {analysis}
                Explore counting principles, permutations, combinations, or probability.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a geometric solution strategy based on:
                {analysis}
                Use coordinate geometry, vector analysis, or trigonometric identities.""",
                context=analysis
            )
        )

        # Step 3: Validation and Refinement
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="""Validate and refine the solution strategy:
                - Check for logical consistency and computational accuracy.
                - Address any gaps or ambiguities.
                - Ensure alignment with the problem's constraints.""",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Synthesis and Decision
        final_strategy = await self.ensemble(
            instruction="""Evaluate and synthesize the refined strategies:
            - Select the most promising approach.
            - Combine insights if multiple strategies are complementary.
            - Ensure the chosen strategy is rigorous and precise.""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Verification
        final_solution = await self.revise(
            instruction="""Perform final verification:
            - Double-check all calculations and logical steps.
            - Ensure the solution meets the problem's requirements.
            - Present the final answer in the required format.""",
            context=final_strategy
        )

        return final_solution