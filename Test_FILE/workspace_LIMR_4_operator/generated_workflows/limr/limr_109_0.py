# Workflow ID: limr_109_0
# Benchmark: limr
# Data Indices: [22, 298]

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
            instruction="""Classify the problem into one or more categories:
            - Geometry, Number Theory, Algebra, Combinatorics, Probability
            - Identify key components, constraints, and solution requirements
            Provide structured classification.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop a solution using geometric reasoning: {classification}",
                context=""
            ),
            self.generate(
                instruction=f"Develop a solution using algebraic manipulation: {classification}",
                context=""
            ),
            self.generate(
                instruction=f"Develop a solution using combinatorial arguments: {classification}",
                context=""
            )
        )

        # Step 3: Refine and Validate Each Strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Critique and improve this solution approach. Ensure all steps are rigorous and valid.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Summarize Key Insights from Each Strategy
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Condense this solution approach into key insights and main steps.",
                context=strategy
            ) for strategy in refined_strategies]
        )

        # Step 5: Ensemble to Select or Synthesize Best Solution
        final_solution = await self.ensemble(
            instruction="Evaluate these approaches and select the most promising solution. If multiple are valid, synthesize them into a unified answer.",
            contexts_list=summaries
        )

        # Step 6: Iterative Refinement Loop
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction="Validate this solution for correctness, completeness, and precision.",
                context=final_solution
            )
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Address issues identified during validation: {validation}",
                    context=final_solution
                )
            else:
                break

        return final_solution