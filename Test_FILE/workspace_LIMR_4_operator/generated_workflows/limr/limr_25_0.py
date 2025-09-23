# Workflow ID: limr_25_0
# Benchmark: limr
# Data Indices: [83, 220]

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

        # Step 1: Analyze the problem to classify type and extract key components
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            1. Classify the problem type (e.g., algebraic, geometric, combinatorial).
            2. Identify all key components (variables, constants, relationships).
            3. Highlight any constraints or special conditions.
            4. Suggest possible solution strategies based on the classification.
            Provide structured output.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Develop an algebraic solution strategy for: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Develop a geometric solution strategy for: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Develop a combinatorial solution strategy for: {analysis}",
                context=analysis
            )
        )

        # Step 3: Refine each strategy iteratively
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction=f"Refine and validate this strategy: {strategy}. Ensure all steps are correct and complete.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Synthesize the best solution from the refined strategies
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            1. Correctness and completeness.
            2. Alignment with the problem's requirements.
            3. Clarity and rigor of reasoning.""",
            contexts_list=refined_strategies
        )

        # Step 5: Final validation
        validated_solution = await self.revise(
            instruction=f"Perform a final validation of this solution: {final_solution}. Ensure it satisfies all constraints and requirements.",
            context=final_solution
        )

        return validated_solution