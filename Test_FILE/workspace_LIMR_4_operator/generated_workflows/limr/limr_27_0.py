# Workflow ID: limr_27_0
# Benchmark: limr
# Data Indices: [44, 209]

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

        # Step 1: Initial Analysis - Classify problem and extract key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify the problem type (geometry, number theory, combinatorics, etc.).
            2. Extract key variables, constraints, and relationships.
            3. Determine the expected solution format (integer, proof, etc.).""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Using the analysis: {initial_analysis}\nSolve using algebraic manipulation.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the analysis: {initial_analysis}\nSolve using geometric transformations.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Using the analysis: {initial_analysis}\nSolve using combinatorial reasoning.",
                context=initial_analysis
            )
        )

        # Step 3: Iterative Refinement - Validate and refine intermediate results
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Validate calculations, check assumptions, and improve clarity.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Final Synthesis - Combine insights and produce the final answer
        final_answer = await self.ensemble(
            instruction="Select the most promising solution or combine complementary insights.",
            contexts_list=refined_strategies
        )

        return final_answer