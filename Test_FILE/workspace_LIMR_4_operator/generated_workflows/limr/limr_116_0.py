# Workflow ID: limr_116_0
# Benchmark: limr
# Data Indices: [244, 52]

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

        # Step 1: Problem Classification and Decomposition
        classification = await self.generate(
            instruction="""Analyze the problem and classify it into one or more categories:
            - Geometry: Shapes, coordinates, transformations
            - Algebra: Equations, inequalities, functions
            - Combinatorics: Counting, probability, permutations
            - Number Theory: Divisibility, primes, modular arithmetic
            Identify key components (e.g., variables, constraints) and suggest potential solution strategies.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = ["Algebraic Manipulation", "Geometric Reasoning", "Combinatorial Analysis", "Number-Theoretic Approach"]
        solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve the problem using {strategy}. Show all steps and justify each transformation.",
                context=classification
            ) for strategy in strategies]
        )

        # Step 3: Validation and Refinement
        refined_solutions = []
        for solution in solutions:
            validation = await self.generate(
                instruction="Validate the solution for logical consistency, arithmetic accuracy, and adherence to constraints.",
                context=solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Correct errors identified in validation: {validation}",
                    context=solution
                )
                refined_solutions.append(refined_solution)
            else:
                refined_solutions.append(solution)

        # Step 4: Ensemble Selection of Best Solution
        final_solution = await self.ensemble(
            instruction="""Select the most robust and accurate solution based on:
            - Completeness of reasoning
            - Adherence to problem constraints
            - Clarity and precision of presentation""",
            contexts_list=refined_solutions
        )

        # Step 5: Summarize Final Answer
        summary = await self.summarize(
            instruction="Condense the final solution into a concise answer, including only the key result.",
            context=final_solution
        )

        return summary