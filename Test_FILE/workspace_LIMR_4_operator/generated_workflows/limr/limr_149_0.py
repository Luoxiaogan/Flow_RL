# Workflow ID: limr_149_0
# Benchmark: limr
# Data Indices: [116, 297]

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
        import re

        # Step 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one of the following categories:
            - Geometry (e.g., shapes, angles, transformations)
            - Number Theory (e.g., primes, divisors, modular arithmetic)
            - Combinatorics (e.g., counting, probability)
            - Algebra (e.g., equations, inequalities, functions)
            - Optimization (e.g., maxima/minima, inequalities)
            - Other (specify)
            
            Identify key features, constraints, and relationships. Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = ["Coordinate Geometry", "Vector Analysis", "Algebraic Manipulation", 
                      "Combinatorial Counting", "Recursive Sequences"]
        candidates = await asyncio.gather(
            *[self.generate(
                instruction=f"Develop a solution using {strategy}. Focus on clarity and precision.",
                context=analysis
            ) for strategy in strategies]
        )

        # Step 3: Synthesis and Selection
        synthesis = await self.ensemble(
            instruction="""Evaluate the candidate solutions:
            - Assess correctness and completeness
            - Compare approaches for elegance and efficiency
            - Identify potential errors or gaps
            Select the most promising solution or combine insights if necessary.""",
            contexts_list=candidates
        )

        # Step 4: Iterative Refinement
        refined_solution = synthesis
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction="Validate the solution. Check calculations, logic, and constraints.",
                context=refined_solution
            )
            if "error" in validation.lower() or "gap" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Address issues identified: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Validation and Output
        final_validation = await self.generate(
            instruction="Perform final checks. Ensure the answer is an integer between 000 and 999.",
            context=refined_solution
        )
        match = re.search(r'\b\d{3}\b', final_validation)
        final_answer = match.group(0) if match else "ERROR: No valid integer found."

        return final_answer