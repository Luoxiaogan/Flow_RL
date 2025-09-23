# Workflow ID: limr_77_0
# Benchmark: limr
# Data Indices: [149, 71]

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

        # Step 1: Initial Analysis - Classify problem and extract key components
        analysis = await self.generate(
            instruction="""Classify this problem and extract key components:
            - Identify the domain (geometry, number theory, algebra, etc.)
            - Extract all numbers, variables, and relationships
            - List explicit and implicit constraints
            - Determine the expected answer format (integer between 000 and 999)
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic manipulation:
                - Simplify equations
                - Perform substitutions
                - Solve for unknowns
                - Verify intermediate results""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using geometric interpretation:
                - Translate into coordinate geometry
                - Apply trigonometric identities
                - Use vector calculations
                - Verify geometric consistency""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using combinatorial reasoning:
                - Apply counting principles
                - Calculate probabilities
                - Use permutations and combinations
                - Verify logical consistency""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using numerical computation:
                - Perform exact calculations
                - Use modular arithmetic if applicable
                - Verify arithmetic accuracy""",
                context=analysis
            )
        )

        # Step 3: Validation and Refinement - Validate and refine each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine this solution:
                - Check for logical consistency
                - Correct arithmetic errors
                - Ensure adherence to constraints
                - Improve clarity and precision""",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesis and Decision - Select the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate and synthesize candidate solutions:
            - Select the most rigorous and accurate solution
            - Combine insights from multiple approaches if necessary
            - Ensure the final answer is an integer between 000 and 999""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Verification - Verify the selected solution
        verified_solution = await self.revise(
            instruction="""Perform final verification:
            - Double-check all calculations
            - Ensure all constraints are satisfied
            - Confirm the answer is an integer between 000 and 999""",
            context=final_solution
        )

        return verified_solution