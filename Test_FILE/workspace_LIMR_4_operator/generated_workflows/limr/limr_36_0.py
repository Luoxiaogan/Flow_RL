# Workflow ID: limr_36_0
# Benchmark: limr
# Data Indices: [215, 227]

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
            instruction="""Classify the problem into one or more categories:
            - Geometry, Number Theory, Combinatorics, Algebra, Optimization, etc.
            Identify key components, constraints, and solution strategies.
            Format as a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = ["Algebraic Manipulation", "Geometric Visualization", 
                      "Combinatorial Enumeration", "Optimization Techniques"]
        candidate_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the problem using {strategy}:
                - Show all steps clearly
                - Maintain precision
                - Highlight assumptions and constraints""",
                context=classification
            ) for strategy in strategies]
        )

        # Step 3: Validation and Refinement
        refined_solutions = []
        for solution in candidate_solutions:
            refined = await self.revise(
                instruction="""Validate and refine the solution:
                - Check calculations for accuracy
                - Close logical gaps
                - Ensure adherence to constraints""",
                context=solution
            )
            refined_solutions.append(refined)

        # Step 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="""Evaluate and synthesize the refined solutions:
            - Select the most correct and elegant solution
            - Ensure the answer is an integer between 000 and 999""",
            contexts_list=refined_solutions
        )

        # Step 5: Final Verification
        verified_solution = await self.revise(
            instruction="""Verify the final solution:
            - Confirm all constraints are satisfied
            - Ensure the format is correct (integer between 000 and 999)""",
            context=final_solution
        )

        return verified_solution