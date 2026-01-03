# Workflow ID: limr_144_0
# Benchmark: limr
# Data Indices: [280, 113]

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

        # Phase 1: Initial Analysis and Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key components (variables, constants, shapes, etc.)
            - Extract constraints and relationships
            - Classify the problem domain (geometry, number theory, etc.)
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Attempt an algebraic solution:
                - Use symbolic manipulation
                - Solve equations systematically
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt a combinatorial solution:
                - Apply counting principles
                - Explore recursive reasoning
                Context: {initial_analysis}""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Attempt a geometric solution:
                - Use coordinate transformations
                - Apply trigonometric identities
                Context: {initial_analysis}""",
                context=initial_analysis
            )
        )

        # Select the best strategy
        best_strategy = await self.ensemble(
            instruction="""Evaluate and select the most promising strategy:
            - Consider completeness and correctness
            - Check alignment with problem constraints
            - Prefer simpler solutions if equally valid""",
            contexts_list=strategies
        )

        # Phase 3: Iterative Refinement
        refined_solution = best_strategy
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction=f"""Validate the current solution:
                - Check for logical consistency
                - Verify arithmetic accuracy
                - Ensure adherence to constraints
                Solution: {refined_solution}""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution to address issues:
                    - Fix identified errors
                    - Add missing details
                    - Improve clarity
                    Issues: {validation}""",
                    context=refined_solution
                )
            else:
                break  # Exit loop if no errors

        # Phase 4: Final Synthesis and Answer Extraction
        final_answer = await self.summarize(
            instruction=f"""Extract the final answer:
            - Condense the solution into a concise format
            - Verify the answer satisfies all constraints
            - Format as an integer between 000 and 999
            Solution: {refined_solution}""",
            context=refined_solution
        )

        return final_answer.strip()