# Workflow ID: limr_32_0
# Benchmark: limr
# Data Indices: [208, 63]

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

        # Phase 1: Initial Analysis and Decomposition
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the problem type (e.g., geometry, number theory, combinatorics).
            - Extract key entities, numbers, relationships, and constraints.
            - Determine the expected answer format and any implicit requirements.
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Attempt algebraic manipulation and equation solving based on: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Apply geometric reasoning and coordinate transformations based on: {analysis}",
                context=analysis
            ),
            self.generate(
                instruction=f"Use combinatorial counting and probabilistic modeling based on: {analysis}",
                context=analysis
            )
        )

        # Phase 3: Iterative Refinement and Validation
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Critique and improve this solution attempt. Ensure all steps are valid and complete.",
                context=strategy
            )
            validated = await self.generate(
                instruction=f"Cross-validate this solution against the problem's constraints: {analysis}",
                context=refined
            )
            refined_strategies.append(validated)

        # Phase 4: Ensemble Decision-Making
        final_solution = await self.ensemble(
            instruction="""Evaluate and synthesize the refined solutions:
            - Select the most accurate and complete solution.
            - Combine complementary insights if applicable.
            - Ensure adherence to the problem's requirements.""",
            contexts_list=refined_strategies
        )

        # Phase 5: Final Verification and Presentation
        verified_solution = await self.revise(
            instruction="Perform a final verification of the solution. Ensure correctness and proper formatting.",
            context=final_solution
        )

        return verified_solution