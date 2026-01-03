# Workflow ID: limr_6_0
# Benchmark: limr
# Data Indices: [169, 19]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Classify this problem:
            - Identify the domain (geometry, number theory, combinatorics, etc.)
            - Extract key components (variables, constraints, relationships)
            - Determine the expected answer format (integer between 000 and 999)
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration
        algebraic_solution = self.generate(
            instruction=f"""Solve using algebraic methods:
            - Perform symbolic manipulation
            - Solve equations
            - Verify intermediate results
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        combinatorial_solution = self.generate(
            instruction=f"""Solve using combinatorial methods:
            - Apply counting principles
            - Explore permutations and combinations
            - Validate logic
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        number_theory_solution = self.generate(
            instruction=f"""Solve using number theory:
            - Apply modular arithmetic
            - Explore divisibility and prime factorization
            - Verify calculations
            Context: {initial_analysis}""",
            context=initial_analysis
        )
        solutions = await asyncio.gather(algebraic_solution, combinatorial_solution, number_theory_solution)

        # Step 3: Intermediate Validation
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution: {sol}",
                context=sol
            ) for sol in solutions]
        )

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="Synthesize the most promising solution from the following options:",
            contexts_list=validated_solutions
        )

        # Step 5: Final Verification
        verified_solution = await self.generate(
            instruction=f"""Verify the final solution:
            - Ensure all constraints are satisfied
            - Check for precision and exactness
            - Format the answer as an integer between 000 and 999
            Context: {final_solution}""",
            context=final_solution
        )

        # Step 6: Output Formatting
        match = re.search(r'\b\d{3}\b', verified_solution)
        final_answer = match.group(0) if match else "Error: No valid answer found"
        return final_answer