# Workflow ID: limr_39_0
# Benchmark: limr
# Data Indices: [248, 115]

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

        # Step 1: Classify the problem type
        classification = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            - Geometry: Involves shapes, coordinates, vectors
            - Number Theory: Involves integers, primes, modular arithmetic
            - Combinatorics: Involves counting, permutations, probability
            - Algebra: Involves equations, polynomials, complex numbers
            Provide a structured classification with reasoning.""",
            context=""
        )

        # Step 2: Generate multiple solution attempts in parallel
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Using synthetic geometry, solve the problem:
                - Break down shapes into simpler components
                - Use geometric properties and theorems
                - Provide step-by-step reasoning""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using coordinate geometry, solve the problem:
                - Assign coordinates to points
                - Use algebraic equations to represent geometric relationships
                - Solve equations systematically""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using number theory, solve the problem:
                - Apply modular arithmetic and divisibility rules
                - Factorize numbers and analyze prime components
                - Provide rigorous proofs""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using combinatorics, solve the problem:
                - Count possibilities using permutations and combinations
                - Calculate probabilities where applicable
                - Ensure all cases are considered""",
                context=classification
            )
        )

        # Step 3: Revise and validate each solution attempt
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution: {sol}",
                context=sol
            ) for sol in solutions]
        )

        # Step 4: Summarize key points from each revised solution
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction=f"Extract key points and conclusions from: {rev_sol}",
                context=rev_sol
            ) for rev_sol in revised_solutions]
        )

        # Step 5: Ensemble to select the best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Correctness and rigor
            - Clarity and completeness
            - Alignment with problem requirements""",
            contexts_list=summaries
        )

        return final_solution