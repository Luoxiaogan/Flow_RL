# Workflow ID: limr_115_0
# Benchmark: limr
# Data Indices: [39, 234]

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

        # Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the main mathematical domain (geometry, number theory, etc.)
            - Extract key components and relationships
            - Classify the problem type
            - Note any special constraints or conditions""",
            context=""
        )
        
        refined_analysis = await self.revise(
            instruction="""Refine the initial analysis:
            - Ensure all components are clearly identified
            - Verify classification accuracy
            - Highlight any missing details or ambiguities""",
            context=initial_analysis
        )

        # Parallel Exploration
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Explore algebraic approach:
                - Use equations and algebraic manipulations
                - Focus on relationships between variables
                - Maintain precision in calculations
                {refined_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Explore geometric approach:
                - Use coordinate geometry or vector analysis
                - Focus on spatial relationships
                - Ensure logical consistency
                {refined_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Explore combinatorial approach:
                - Use counting principles and probability
                - Focus on discrete structures
                - Ensure all cases are considered
                {refined_analysis}""",
                context=""
            )
        )

        critiqued_approaches = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique this approach:
                - Verify all calculations
                - Ensure logical consistency
                - Highlight any errors or gaps
                {approach}""",
                context=approach
            ) for approach in approaches]
        )

        # Synthesis and Decision
        best_approach = await self.ensemble(
            instruction="""Select the best approach:
            - Consider elegance and efficiency
            - Ensure completeness and correctness
            - Choose the approach that best fits the problem structure""",
            contexts_list=critiqued_approaches
        )

        # Iterative Refinement
        refined_solution = best_approach
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the solution:
                - Check against problem constraints
                - Verify all steps
                - Ensure final answer format is correct
                {refined_solution}""",
                context=""
            )
            
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution:
                    - Address validation issues: {validation}
                    - Correct any errors
                    - Improve clarity and precision""",
                    context=refined_solution
                )
            else:
                break

        # Final Validation
        final_validation = await self.generate(
            instruction=f"""Final validation:
            - Ensure solution meets all problem requirements
            - Verify final answer format (integer 000-999)
            - Confirm logical consistency
            {refined_solution}""",
            context=""
        )

        if "error" in final_validation.lower():
            raise ValueError("Final validation failed. Solution may be incorrect.")
        
        return refined_solution