# Workflow ID: limr_13_0
# Benchmark: limr
# Data Indices: [282, 167]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure and classify it into one of the following categories:
            - Geometry: Involves shapes, angles, distances, or coordinates.
            - Number Theory: Involves integers, modular arithmetic, divisibility, or primes.
            - Combinatorics: Involves counting, permutations, combinations, or probability.
            - Algebra: Involves equations, polynomials, or functional relationships.
            - Optimization: Involves finding maxima/minima or extremal values.
            Provide a clear classification and identify key components such as variables, constraints, and objectives.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the analysis: {analysis}
                Develop a solution using geometric reasoning. Focus on angle relationships, symmetry, or coordinate geometry.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis: {analysis}
                Develop a solution using number-theoretic reasoning. Consider modular arithmetic, divisibility, or prime factorization.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis: {analysis}
                Develop a solution using combinatorial reasoning. Apply counting principles, permutations, or probabilistic arguments.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis: {analysis}
                Develop a solution using algebraic reasoning. Solve equations, manipulate polynomials, or analyze functional relationships.""",
                context=analysis
            )
        )

        # Step 3: Validation and Iterative Refinement
        validated_strategies = []
        for strategy in strategies:
            validation = await self.generate(
                instruction=f"""Validate the following solution strategy: {strategy}
                Check for logical consistency, precision, and adherence to problem constraints. Identify any errors or gaps.""",
                context=strategy
            )
            if "error" in validation.lower():
                refined_strategy = await self.revise(
                    instruction=f"""Revise the solution strategy to address the following issues: {validation}
                    Ensure all steps are correct and complete.""",
                    context=strategy
                )
                validated_strategies.append(refined_strategy)
            else:
                validated_strategies.append(strategy)

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the results from all valid solution strategies:
            - Compare answers for consistency.
            - Resolve discrepancies by identifying the most robust approach.
            - Present the final answer as an integer between 000 and 999.""",
            contexts_list=validated_strategies
        )

        return final_solution