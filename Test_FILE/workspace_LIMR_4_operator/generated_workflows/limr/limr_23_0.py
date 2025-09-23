# Workflow ID: limr_23_0
# Benchmark: limr
# Data Indices: [288, 55]

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
        classification = await self.generate(
            instruction="""Classify the problem into one of the following domains:
            - Geometry
            - Number Theory
            - Combinatorics
            - Algebra
            - Optimization
            - Sequence and Series
            
            Identify key components, variables, and constraints. Format as:
            Domain: [domain]
            Variables: [list of variables]
            Constraints: [list of constraints]""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        decomposition = await self.generate(
            instruction=f"""Break the problem into sub-problems based on its classification:
            Classification: {classification}
            
            For each sub-problem, identify:
            - What needs to be solved
            - Relevant formulas or theorems
            - Dependencies on other sub-problems""",
            context=classification
        )

        # Step 3: Parallel Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using method 1: [details of method 1]
                Problem: {self.problem_text}
                Decomposition: {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using method 2: [details of method 2]
                Problem: {self.problem_text}
                Decomposition: {decomposition}""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Solve using method 3: [details of method 3]
                Problem: {self.problem_text}
                Decomposition: {decomposition}""",
                context=decomposition
            )
        )

        # Step 4: Iterative Refinement
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Validate and refine the solution. Ensure all steps are logically sound and calculations are correct.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 5: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="Select the best solution or synthesize insights from all strategies. Ensure the final answer is an integer between 000 and 999.",
            contexts_list=refined_strategies
        )

        # Step 6: Final Verification
        verified_solution = await self.revise(
            instruction="Verify the final solution against all constraints and ensure it matches the expected format.",
            context=final_solution
        )

        return verified_solution