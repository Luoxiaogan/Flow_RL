# Workflow ID: limr_83_0
# Benchmark: limr
# Data Indices: [1, 53]

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
            instruction="""Decompose the problem into its core components:
            - Identify the problem type (geometry, number theory, etc.)
            - Extract key variables and constraints
            - Highlight any special cases or edge conditions
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a solution using algebraic methods:
                {decomposition}
                Show all steps and justify each transformation.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Develop a solution using geometric reasoning:
                {decomposition}
                Use visual or spatial intuition where applicable.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Develop a solution using combinatorial techniques:
                {decomposition}
                Apply counting principles or probabilistic reasoning.""",
                context=decomposition
            )
        )

        # Step 3: Refine Each Strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Critique and improve this solution. Ensure all steps are valid and complete.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Verify Intermediate Results
        verifications = await asyncio.gather(
            *[self.generate(
                instruction="Verify the correctness of this solution. Check for logical gaps or errors.",
                context=strategy
            ) for strategy in refined_strategies]
        )

        # Step 5: Ensemble to Select the Best Solution
        final_solution = await self.ensemble(
            instruction="""Select the most robust and accurate solution:
            - Consider completeness and clarity
            - Ensure the solution meets all problem constraints
            - Prefer exact results over approximations""",
            contexts_list=refined_strategies
        )

        # Step 6: Summarize the Final Answer
        summary = await self.summarize(
            instruction="Condense the final solution into a concise answer. Ensure it is precise and formatted correctly.",
            context=final_solution
        )

        return summary