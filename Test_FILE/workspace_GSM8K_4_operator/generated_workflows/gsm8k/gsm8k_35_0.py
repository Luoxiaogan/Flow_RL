# Workflow ID: gsm8k_35_0
# Benchmark: gsm8k
# Data Indices: [266, 124]

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

        # Step 1: Initial Analysis and Problem Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Extract all numerical values and their context.
            - Identify entities, relationships, and constraints.
            - Classify the problem type (e.g., rate, distribution, proportion).
            - Highlight any ambiguities or implicit assumptions.
            Present findings in a structured format.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        direct_computation = self.generate(
            instruction=f"""Solve the problem step-by-step using arithmetic operations:
            - Follow the sequence of calculations implied by the problem.
            - Show intermediate results with clear explanations.
            - Ensure numerical exactness at each step.
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )
        
        unit_analysis = self.generate(
            instruction=f"""Perform unit analysis:
            - Verify consistency in units and dimensions.
            - Convert units if necessary.
            - Highlight any unit-related issues.
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )
        
        estimation = self.generate(
            instruction=f"""Provide rough estimates to validate the solution:
            - Use order-of-magnitude reasoning.
            - Compare estimates with expected results.
            - Flag any significant discrepancies.
            Problem context: {initial_analysis}""",
            context=initial_analysis
        )
        
        # Execute strategies in parallel
        strategies = await asyncio.gather(direct_computation, unit_analysis, estimation)

        # Step 3: Conditional Branching for Refinement
        validation = await self.generate(
            instruction="""Validate the outputs of the parallel strategies:
            - Check for consistency across solutions.
            - Identify any errors or discrepancies.
            - Determine if refinement is needed.""",
            context="\n".join(strategies)
        )

        if "error" in validation.lower() or "discrepancy" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Refine the solution based on validation feedback:
                - Address identified errors or discrepancies.
                - Clarify ambiguous steps.
                - Ensure all intermediate results are accurate.
                Validation report: {validation}""",
                context=strategies[0]  # Start with the primary strategy
            )
            strategies[0] = refined_solution  # Update primary strategy

        # Step 4: Synthesis and Final Validation
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Select the most accurate and consistent approach.
            - Combine insights from all strategies if necessary.
            - Ensure the final answer meets the problem's requirements.""",
            contexts_list=strategies
        )

        # Step 5: Extract and Return Numerical Answer
        numerical_answer = await self.generate(
            instruction="""Extract the final numerical answer:
            - Ensure the answer is a single numerical value.
            - Include units if applicable.
            Final solution: {final_solution}""",
            context=final_solution
        )

        return numerical_answer