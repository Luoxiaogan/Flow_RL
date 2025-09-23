# Workflow ID: limr_44_0
# Benchmark: limr
# Data Indices: [9, 178]

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

        # Step 1: Hierarchical Decomposition
        decomposition = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the main problem type (geometry, algebra, etc.)
            - Break it into sub-problems
            - Highlight key variables, constraints, and relationships
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using an algebraic approach:
                - Translate the problem into equations
                - Solve step-by-step
                - Validate intermediate results""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using a geometric approach:
                - Visualize the problem
                - Use geometric properties and theorems
                - Validate intermediate results""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using a combinatorial approach:
                - Count possibilities systematically
                - Use permutations, combinations, or probability principles
                - Validate intermediate results""",
                context=decomposition
            )
        )

        # Step 3: Synthesize Best Path
        synthesis = await self.ensemble(
            instruction="""Evaluate all approaches:
            - Assess correctness and completeness
            - Choose the most promising path
            - Highlight any gaps or uncertainties""",
            contexts_list=strategies
        )

        # Step 4: Sequential Refinement
        refined_solution = await self.revise(
            instruction="""Refine the selected solution:
            - Correct errors
            - Add missing details
            - Ensure logical consistency and precision""",
            context=synthesis
        )

        # Step 5: Final Validation
        validation = await self.generate(
            instruction="""Validate the final solution:
            - Verify all steps
            - Check against constraints and conditions
            - Confirm the answer format is correct""",
            context=refined_solution
        )

        # Step 6: Summarize Key Insights
        summary = await self.summarize(
            instruction="""Summarize the solution:
            - Highlight key steps
            - Present the final answer clearly
            - Include any important insights""",
            context=validation
        )

        return summary