# Workflow ID: limr_8_0
# Benchmark: limr
# Data Indices: [187, 217]

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

        # Step 1: Classify the problem and extract key components
        classification = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            - Geometry (e.g., shapes, angles, distances)
            - Number Theory (e.g., primes, divisors, modular arithmetic)
            - Algebra (e.g., equations, polynomials, functions)
            - Combinatorics (e.g., counting, permutations, probabilities)
            - Optimization (e.g., maxima/minima, inequalities)
            
            Extract all key entities, relationships, and constraints. Format as:
            Category: [classification]
            Entities: [list of entities]
            Relationships: [descriptions of relationships]
            Constraints: [explicit and implicit constraints]""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using synthetic reasoning, solve the problem:
                Classification: {classification}
                Focus on geometric intuition and properties of shapes.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using algebraic manipulation, solve the problem:
                Classification: {classification}
                Focus on equations, substitutions, and symbolic transformations.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using numerical computation, solve the problem:
                Classification: {classification}
                Focus on precise calculations and numeric methods.""",
                context=classification
            )
        )

        # Step 3: Validate and refine each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution attempt:\n{strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Select the most complete, rigorous, and efficient solution:
            Consider:
            - Does the solution address all parts of the problem?
            - Are all steps logically sound and mathematically valid?
            - Is the solution concise and elegant?""",
            contexts_list=refined_strategies
        )

        # Step 5: Prepare the final output
        formatted_output = await self.generate(
            instruction=f"""Format the final solution as required:
            Ensure the answer is an integer between 000 and 999, boxed appropriately.
            Final Solution: {final_solution}""",
            context=final_solution
        )

        return formatted_output