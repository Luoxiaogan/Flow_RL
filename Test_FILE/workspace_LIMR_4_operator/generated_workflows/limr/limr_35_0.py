# Workflow ID: limr_35_0
# Benchmark: limr
# Data Indices: [276, 272]

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

        # Step 1: Initial Analysis - Decompose the problem into key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the mathematical domain (e.g., geometry, number theory).
            - Extract all given variables, constraints, and objectives.
            - Highlight any ambiguities or missing information.
            - Suggest potential solution strategies.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Attempt an algebraic solution:
                - Translate the problem into equations or expressions.
                - Solve step-by-step, showing all intermediate calculations.
                - Validate the solution against the problem's constraints.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt a geometric interpretation:
                - Visualize the problem using diagrams or coordinate systems.
                - Apply geometric principles (e.g., symmetry, congruence).
                - Derive the solution and verify its correctness.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt a combinatorial or probabilistic approach:
                - Enumerate possible cases or outcomes.
                - Apply counting principles or probability rules.
                - Ensure the solution aligns with the problem's requirements.""",
                context=initial_analysis
            )
        )

        # Step 3: Iterative Refinement of Each Strategy
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="""Critique and improve the solution:
                - Check for logical consistency and mathematical rigor.
                - Fill in any missing steps or details.
                - Resolve any identified ambiguities.""",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Ensemble Decision-Making - Select the Best Solution
        final_solution = await self.ensemble(
            instruction="""Evaluate and synthesize the solutions:
            - Compare the rigor, clarity, and efficiency of each approach.
            - Select the most appropriate solution based on the problem's requirements.
            - Provide justification for the chosen solution.""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Validation and Presentation
        validated_solution = await self.revise(
            instruction="""Ensure the final solution is complete and correct:
            - Verify all calculations and logical steps.
            - Confirm the solution matches the expected format (e.g., integer between 000 and 999).
            - Present the solution in a clear and concise manner.""",
            context=final_solution
        )

        return validated_solution