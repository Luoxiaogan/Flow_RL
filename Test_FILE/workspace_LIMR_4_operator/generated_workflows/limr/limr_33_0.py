# Workflow ID: limr_33_0
# Benchmark: limr
# Data Indices: [142, 152]

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

        # Initial analysis to understand the problem structure
        initial_analysis = await self.generate(
            instruction="""Analyze the problem to identify:
            - Main mathematical domain (geometry, number theory, etc.)
            - Key components and variables
            - Constraints and conditions
            - Expected answer format
            Provide a structured breakdown.""",
            context=""
        )

        # Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Develop a solution using algebraic techniques.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Develop a solution using geometric reasoning.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the analysis: {initial_analysis}
                Develop a solution using combinatorial methods.""",
                context=initial_analysis
            )
        )

        # Validate and refine each strategy iteratively
        refined_strategies = []
        for strategy in strategies:
            refined = strategy
            for _ in range(3):  # Allow up to 3 refinement iterations
                validation = await self.generate(
                    instruction=f"""Validate the solution: {refined}
                    Check for:
                    - Logical consistency
                    - Mathematical correctness
                    - Alignment with problem constraints""",
                    context=refined
                )
                if "error" in validation.lower():
                    refined = await self.revise(
                        instruction=f"""Revise the solution to fix: {validation}""",
                        context=refined
                    )
                else:
                    break
            refined_strategies.append(refined)

        # Synthesize the best solution from refined strategies
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Completeness and rigor
            - Alignment with problem requirements
            - Clarity and precision""",
            contexts_list=refined_strategies
        )

        return final_solution