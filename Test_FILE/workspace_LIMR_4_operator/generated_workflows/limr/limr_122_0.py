# Workflow ID: limr_122_0
# Benchmark: limr
# Data Indices: [28, 133]

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

        # Step 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one of the following categories:
            - Geometry
            - Number Theory
            - Algebra
            - Combinatorics
            - Optimization
            Identify key components, constraints, and solution requirements.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Solve using algebraic manipulation and equations.",
                context=analysis
            ),
            self.generate(
                instruction="Solve using geometric reasoning and spatial analysis.",
                context=analysis
            ),
            self.generate(
                instruction="Solve using combinatorial arguments and counting principles.",
                context=analysis
            )
        )

        # Step 3: Iterative Refinement and Validation
        refined_solutions = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Critique and refine the solution. Ensure clarity, rigor, and correctness.",
                context=strategy
            )
            summarized = await self.summarize(
                instruction="Condense the refined solution into key insights.",
                context=refined
            )
            refined_solutions.append(summarized)

        # Step 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="Evaluate the refined solutions and select the most robust and well-supported one.",
            contexts_list=refined_solutions
        )

        # Step 5: Handle Edge Cases and Special Constraints
        edge_case_handling = await self.revise(
            instruction="Revisit the solution to ensure all edge cases and constraints are addressed.",
            context=final_solution
        )

        return edge_case_handling