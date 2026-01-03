# Workflow ID: limr_129_0
# Benchmark: limr
# Data Indices: [172, 93]

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

        # Step 1: Initial Analysis - Decompose the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key components (variables, equations, constraints)
            - Classify the problem type (algebraic, geometric, combinatorial, etc.)
            - Highlight any ambiguities or missing information
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using algebraic methods:
                - Perform symbolic manipulations
                - Solve equations step-by-step
                - Verify intermediate results
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using combinatorial reasoning:
                - Count possibilities systematically
                - Apply probability principles if applicable
                - Validate logic and consistency
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve using geometric interpretation:
                - Visualize shapes and relationships
                - Apply coordinate geometry or trigonometric identities
                - Cross-check calculations
                Context: {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Step 3: Ensemble Decision - Synthesize the best solution
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Combine insights from all approaches
            - Resolve contradictions
            - Ensure logical consistency and completeness
            Select the most rigorous and accurate result.""",
            contexts_list=approaches
        )

        # Step 4: Iterative Refinement - Improve the solution
        refined_solution = synthesized_solution
        for _ in range(3):  # Maximum of 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                - Check against the original problem statement
                - Verify all steps and calculations
                - Identify any remaining issues
                Current solution: {refined_solution}""",
                context=refined_solution
            )
            if "error" not in validation.lower():
                break  # Stop if no errors are found
            refined_solution = await self.revise(
                instruction=f"""Refine the solution:
                - Address identified issues
                - Clarify ambiguous steps
                - Improve rigor and precision
                Issues: {validation}
                Current solution: {refined_solution}""",
                context=refined_solution
            )

        # Step 5: Final Verification - Ensure correctness
        final_verification = await self.generate(
            instruction=f"""Perform final verification:
            - Confirm the solution satisfies all problem constraints
            - Cross-check calculations and logic
            - Present the final answer in the required format
            Current solution: {refined_solution}""",
            context=refined_solution
        )

        return final_verification