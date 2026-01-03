# Workflow ID: limr_81_0
# Benchmark: limr
# Data Indices: [151, 3]

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

        # Step 1: Problem Classification
        classification = await self.generate(
            instruction="""Classify this problem into one or more categories:
            - Geometry, Algebra, Number Theory, Combinatorics, Probability, etc.
            - Identify key characteristics and constraints.
            - Suggest potential solution strategies.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        sub_problems = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Break the problem into smaller sub-problems:
            - Define each sub-problem clearly.
            - Identify dependencies between sub-problems.
            - Suggest the order of solving sub-problems.""",
            context=classification
        )

        # Step 3: Parallel Exploration of Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using Strategy 1 (Mathematical Analysis):
                {sub_problems}""",
                context=sub_problems
            ),
            self.generate(
                instruction=f"""Solve using Strategy 2 (Logical Reasoning):
                {sub_problems}""",
                context=sub_problems
            ),
            self.generate(
                instruction=f"""Solve using Strategy 3 (Creative Insights):
                {sub_problems}""",
                context=sub_problems
            )
        )

        # Step 4: Iterative Refinement
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Improve clarity, verify calculations, and add missing details.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the refined strategies:
            - Evaluate correctness and completeness.
            - Ensure the final answer is an integer between 000 and 999.
            - Provide justification for the chosen solution.""",
            contexts_list=refined_strategies
        )

        return final_solution