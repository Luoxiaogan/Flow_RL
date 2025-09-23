# Workflow ID: limr_100_0
# Benchmark: limr
# Data Indices: [249, 242]

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

        # Step 1: Initial Analysis - Classify and Decompose
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify the domain (geometry, number theory, etc.)
            2. Extract key variables, constraints, and relationships
            3. Suggest potential solution strategies
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate Multiple Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"Explore solution using algebraic methods: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Explore solution using geometric methods: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Explore solution using combinatorial methods: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Critique Each Path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"Improve clarity, rigor, and correctness: {path}",
                context=path
            ) for path in paths]
        )

        # Step 4: Synthesis - Combine Paths into Unified Solution
        synthesis = await self.ensemble(
            instruction="""Synthesize the refined paths:
            1. Resolve contradictions
            2. Select the most robust approach
            3. Ensure coherence and completeness""",
            contexts_list=refined_paths
        )

        # Step 5: Iterative Refinement - Validate Final Output
        for _ in range(3):  # Allow up to 3 refinement cycles
            validation = await self.generate(
                instruction=f"Validate the solution: {synthesis}",
                context=synthesis
            )
            if "error" in validation.lower():
                synthesis = await self.revise(
                    instruction=f"Fix issues identified: {validation}",
                    context=synthesis
                )
            else:
                break

        return synthesis