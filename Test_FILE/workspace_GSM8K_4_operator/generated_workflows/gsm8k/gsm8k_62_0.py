# Workflow ID: gsm8k_62_0
# Benchmark: gsm8k
# Data Indices: [221, 136]

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
            - Extract all numbers and their context
            - Identify relationships between quantities
            - Classify the problem type (rate, proportion, distribution, etc.)
            - Highlight what the question asks for
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct computation:
                - Perform step-by-step calculations
                - Show intermediate results
                - Ensure numerical precision
                Context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using proportional reasoning:
                - Identify ratios or fractions
                - Scale quantities appropriately
                - Validate consistency
                Context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using unit conversion or scaling:
                - Convert units where necessary
                - Adjust quantities proportionally
                - Verify logical consistency
                Context: {analysis}""",
                context=analysis
            )
        )

        # Step 3: Iterative Refinement
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Critique and improve this solution. Address errors or missing details.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Ensemble Decision
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Evaluate numerical correctness
            - Check logical consistency
            - Align with problem context
            Choose the most accurate and complete answer.""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Output
        final_answer = await self.summarize(
            instruction="Condense the final solution into a single numerical value.",
            context=final_solution
        )

        return final_answer