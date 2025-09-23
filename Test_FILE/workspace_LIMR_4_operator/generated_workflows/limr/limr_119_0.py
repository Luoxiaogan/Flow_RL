# Workflow ID: limr_119_0
# Benchmark: limr
# Data Indices: [129, 2]

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
            instruction="""Analyze the problem:
            - Classify the problem type (geometry, algebra, combinatorics, etc.)
            - Identify key components (variables, constraints, relationships)
            - Highlight any special cases or edge conditions
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration
        algebraic_solution = self.generate(
            instruction=f"""Solve using algebraic methods:
            - Simplify expressions
            - Solve equations
            - Verify intermediate steps
            Problem analysis: {analysis}""",
            context=""
        )
        geometric_solution = self.generate(
            instruction=f"""Solve using geometric reasoning:
            - Analyze shapes and spatial relationships
            - Apply geometric theorems
            - Verify intermediate steps
            Problem analysis: {analysis}""",
            context=""
        )
        combinatorial_solution = self.generate(
            instruction=f"""Solve using combinatorial methods:
            - Count possibilities
            - Enumerate cases
            - Verify intermediate steps
            Problem analysis: {analysis}""",
            context=""
        )
        solutions = await asyncio.gather(algebraic_solution, geometric_solution, combinatorial_solution)

        # Step 3: Intermediate Validation
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the solution:
                - Check calculations
                - Ensure logical consistency
                - Address any errors or ambiguities
                Original solution: {sol}""",
                context=sol
            ) for sol in solutions]
        )

        # Step 4: Ensemble Selection
        final_solution = await self.ensemble(
            instruction="""Compare and synthesize the validated solutions:
            - Select the most complete and accurate solution
            - Combine insights from multiple approaches if necessary
            - Ensure the final answer is an integer between 000 and 999""",
            contexts_list=validated_solutions
        )

        # Step 5: Iterative Refinement (if needed)
        refined_solution = final_solution
        for _ in range(2):  # Limit iterations to avoid infinite loops
            refinement = await self.revise(
                instruction=f"""Refine the solution:
                - Incorporate additional insights
                - Address remaining ambiguities
                Current solution: {refined_solution}""",
                context=refined_solution
            )
            if refinement == refined_solution:  # No further changes
                break
            refined_solution = refinement

        # Step 6: Final Verification
        verified_solution = await self.revise(
            instruction=f"""Perform final verification:
            - Ensure all constraints are satisfied
            - Confirm the answer format (integer between 000 and 999)
            Final solution: {refined_solution}""",
            context=refined_solution
        )

        return verified_solution