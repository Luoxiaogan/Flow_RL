# Workflow ID: limr_106_0
# Benchmark: limr
# Data Indices: [70, 23]

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
            1. Classify the problem type (algebraic, geometric, combinatorial, etc.).
            2. Identify key components (variables, equations, constraints).
            3. Highlight any special properties or symmetries.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Solve using algebraic manipulation (focus on equations, variables).",
                context=analysis
            ),
            self.generate(
                instruction="Solve using geometric interpretation (focus on shapes, coordinates).",
                context=analysis
            ),
            self.generate(
                instruction="Solve using combinatorial reasoning (focus on counting, arrangements).",
                context=analysis
            ),
            self.generate(
                instruction="Solve using number-theoretic techniques (focus on primes, divisors).",
                context=analysis
            )
        )

        # Step 3: Intermediate Validation
        validations = await asyncio.gather(
            *[self.generate(
                instruction=f"Validate this solution: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Refinement
        refined_solutions = []
        for i, validation in enumerate(validations):
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=strategies[i]
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(strategies[i])

        # Step 5: Synthesis and Decision
        final_solution = await self.ensemble(
            instruction="Select the most promising solution or synthesize complementary insights.",
            contexts_list=refined_solutions
        )

        # Step 6: Final Verification
        verified_solution = await self.revise(
            instruction="Verify precision and correctness. Ensure the answer is an exact integer between 000 and 999.",
            context=final_solution
        )

        return verified_solution