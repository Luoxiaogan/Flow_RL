# Workflow ID: limr_40_0
# Benchmark: limr
# Data Indices: [92, 218]

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

        # Step 1: Initial Analysis and Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one of the following categories:
            - Algebraic (equations, polynomials, functional equations)
            - Geometric (2D/3D geometry, coordinate systems, vectors)
            - Combinatorial (counting principles, permutations, probability)
            - Number Theory (modular arithmetic, primes, divisibility)
            - Optimization (maxima/minima, inequalities)
            
            Identify key components such as variables, constraints, relationships, and expected answer format. Propose potential solution strategies.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        approaches = ["Algebraic", "Geometric", "Combinatorial", "Number Theory", "Optimization"]
        solution_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"Attempt to solve the problem using {approach} techniques. Focus on clear reasoning and precise calculations.",
                context=initial_analysis
            ) for approach in approaches]
        )

        # Step 3: Validation and Refinement
        refined_solutions = []
        for attempt in solution_attempts:
            validation = await self.revise(
                instruction="Validate the solution for logical consistency, mathematical correctness, and adherence to constraints. Highlight any issues.",
                context=attempt
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction="Refine the solution to address identified issues. Ensure all steps are rigorous and well-supported.",
                    context=validation
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(validation)

        # Step 4: Synthesis and Selection
        final_solution = await self.ensemble(
            instruction="""Compare and synthesize the refined solutions. Select the best approach based on:
            - Accuracy and correctness
            - Clarity and logical flow
            - Alignment with problem requirements
            Provide the final answer in the required format (integer between 000 and 999).""",
            contexts_list=refined_solutions
        )

        # Step 5: Final Output Formatting
        formatted_output = await self.summarize(
            instruction="Condense the final solution into a concise and precise format. Ensure the answer is an integer between 000 and 999.",
            context=final_solution
        )

        return formatted_output