# Workflow ID: limr_99_0
# Benchmark: limr
# Data Indices: [229, 144]

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

        # Step 1: Classify the problem and extract key components
        classification = await self.generate(
            instruction="""Classify the problem into one of the following categories:
            - Geometry (e.g., 3D geometry, coordinate geometry)
            - Number Theory (e.g., modular arithmetic, divisibility)
            - Combinatorics (e.g., counting principles, probability)
            - Algebra (e.g., polynomial equations, functional equations)
            - Optimization (e.g., maxima/minima, inequalities)
            - Sequence/Series (e.g., recursive sequences, summations)
            
            Identify key components such as variables, constraints, and goals. Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction="Develop an algebraic solution strategy.",
                context=classification
            ),
            self.generate(
                instruction="Develop a geometric solution strategy.",
                context=classification
            ),
            self.generate(
                instruction="Develop a combinatorial solution strategy.",
                context=classification
            )
        )

        # Step 3: Refine each strategy independently
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine the following strategy:\n{strategy}\nEnsure logical consistency and precision.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Ensemble to select the best strategy
        best_strategy = await self.ensemble(
            instruction="Select the most promising strategy based on clarity, rigor, and alignment with problem requirements.",
            contexts_list=refined_strategies
        )

        # Step 5: Implement the chosen strategy with iterative refinement
        solution = await self.generate(
            instruction=f"Implement the chosen strategy:\n{best_strategy}\nShow all steps and calculations.",
            context=best_strategy
        )

        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the solution for correctness, precision, and adherence to constraints.",
                context=solution
            )
            if "error" in validation.lower():
                solution = await self.revise(
                    instruction=f"Fix issues identified in validation:\n{validation}",
                    context=solution
                )
            else:
                break

        # Step 6: Finalize the answer
        final_answer = await self.generate(
            instruction="Extract the final answer as an integer between 000 and 999. Ensure it is boxed and clearly labeled.",
            context=solution
        )

        return final_answer