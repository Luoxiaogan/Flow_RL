# Workflow ID: limr_64_0
# Benchmark: limr
# Data Indices: [48, 299]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        """
        # --- ALL IMPORTS MUST GO HERE INSIDE THE METHOD ---
        import asyncio

        # Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify the main mathematical domain (geometry, algebra, etc.)
            2. Extract key variables and constraints
            3. Determine potential solution strategies
            Provide a structured breakdown.""",
            context=""
        )

        # Parallel Solution Attempts
        algebraic_attempt = self.generate(
            instruction=f"""Attempt an algebraic solution:
            - Set up equations based on extracted variables
            - Solve step-by-step
            - Verify intermediate results
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        geometric_attempt = self.generate(
            instruction=f"""Attempt a geometric solution:
            - Use coordinate geometry or trigonometric identities
            - Visualize the problem
            - Calculate necessary values
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        combinatorial_attempt = self.generate(
            instruction=f"""Attempt a combinatorial solution:
            - Count possibilities
            - Apply probability principles
            - Verify logical consistency
            Context: {initial_analysis}""",
            context=initial_analysis
        )

        attempts = await asyncio.gather(algebraic_attempt, geometric_attempt, combinatorial_attempt)

        # Iterative Refinement
        refined_attempts = []
        for attempt in attempts:
            validation = await self.generate(
                instruction=f"Validate the solution attempt: {attempt}",
                context=attempt
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix issues identified in validation: {validation}",
                    context=attempt
                )
            else:
                refined = attempt
            refined_attempts.append(refined)

        # Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="Select the best solution based on correctness, completeness, and elegance",
            contexts_list=refined_attempts
        )

        return final_solution