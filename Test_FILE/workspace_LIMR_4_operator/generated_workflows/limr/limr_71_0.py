# Workflow ID: limr_71_0
# Benchmark: limr
# Data Indices: [109, 50]

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
            instruction="""Analyze the problem and extract key components:
            - Identify problem type (geometry, number theory, combinatorics, etc.)
            - Extract variables, constraints, and relationships
            - Classify required solution strategies
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"Using algebraic methods, solve the problem: {decomposition}",
                context=decomposition
            ),
            self.generate(
                instruction=f"Using geometric interpretation, solve the problem: {decomposition}",
                context=decomposition
            ),
            self.generate(
                instruction=f"Using combinatorial reasoning, solve the problem: {decomposition}",
                context=decomposition
            )
        )

        # Step 3: Iterative Refinement
        refined_approaches = []
        for approach in approaches:
            refined = approach
            for _ in range(3):  # Maximum of 3 refinement iterations
                critique = await self.revise(
                    instruction="Identify errors, gaps, or areas for improvement.",
                    context=refined
                )
                if "error" not in critique.lower():
                    break
                refined = await self.revise(
                    instruction=f"Improve solution based on critique: {critique}",
                    context=refined
                )
            refined_approaches.append(refined)

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="Select the most rigorous and complete solution or synthesize insights from multiple approaches.",
            contexts_list=refined_approaches
        )

        # Step 5: Final Validation
        validation = await self.generate(
            instruction=f"Validate the final solution against the original problem: {final_solution}",
            context=self.problem_text
        )

        return validation