# Workflow ID: limr_94_0
# Benchmark: limr
# Data Indices: [235, 12]

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

        # Step 1: Problem Decomposition
        decomposition = await self.generate(
            instruction="""Analyze the problem to identify:
            - Key entities (numbers, variables, relationships)
            - Constraints and conditions
            - Problem type (geometry, number theory, combinatorics, etc.)
            - Expected solution format
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the decomposition: {decomposition}
                Develop a solution using algebraic methods.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Using the decomposition: {decomposition}
                Develop a solution using combinatorial methods.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Using the decomposition: {decomposition}
                Develop a solution using geometric methods.""",
                context=decomposition
            )
        )

        # Step 3: Refine Each Strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Critique and refine this solution for correctness and clarity.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="""Evaluate the refined solutions:
            - Check logical consistency
            - Verify adherence to constraints
            - Select the most complete and correct solution""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Validation and Formatting
        validated_solution = await self.revise(
            instruction="""Ensure the solution is precise and formatted correctly:
            - Final answer must be an integer between 000 and 999
            - No approximations allowed""",
            context=final_solution
        )

        return validated_solution