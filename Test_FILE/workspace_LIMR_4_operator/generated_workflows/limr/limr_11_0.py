# Workflow ID: limr_11_0
# Benchmark: limr
# Data Indices: [274, 111]

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

        # Phase 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem and classify it into categories:
            - Geometry: Involves shapes, coordinates, or spatial relationships
            - Number Theory: Involves integers, primes, or modular arithmetic
            - Algebra: Involves equations, functions, or inequalities
            - Combinatorics: Involves counting, permutations, or probability
            - Optimization: Involves finding maxima/minima or extremal values
            
            Provide a structured classification with key features and constraints.""",
            context=""
        )

        # Phase 2: Parallel Exploration of Solution Strategies
        strategies = [
            "Algebraic manipulation and equation solving.",
            "Geometric reasoning and coordinate transformations.",
            "Combinatorial enumeration and probabilistic analysis.",
            "Optimization techniques and inequality applications."
        ]
        parallel_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve the problem using {strategy}. Show all steps and justify each transformation.",
                context=analysis
            ) for strategy in strategies]
        )

        # Phase 3: Ensemble Synthesis
        refined_attempts = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine this solution. Ensure all steps are valid and well-justified.",
                context=attempt
            ) for attempt in parallel_attempts]
        )
        best_solution = await self.ensemble(
            instruction="Evaluate and synthesize the best solution. Combine complementary insights and resolve inconsistencies.",
            contexts_list=refined_attempts
        )

        # Phase 4: Iterative Refinement
        final_solution = best_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate this solution against the problem statement and constraints. Identify any errors or gaps.",
                context=final_solution
            )
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Revise the solution to address: {validation}",
                    context=final_solution
                )
            else:
                break

        # Phase 5: Final Validation and Output
        final_output = await self.summarize(
            instruction="Condense the solution into a concise format. Include only the final answer and key reasoning steps.",
            context=final_solution
        )

        return final_output