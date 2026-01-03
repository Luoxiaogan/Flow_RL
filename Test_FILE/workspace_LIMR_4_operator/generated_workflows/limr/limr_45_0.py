# Workflow ID: limr_45_0
# Benchmark: limr
# Data Indices: [175, 213]

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

        # Phase 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one of the following categories:
            - Geometry (e.g., 3D geometry, coordinate geometry)
            - Number Theory (e.g., modular arithmetic, divisibility)
            - Algebra (e.g., polynomial equations, functional equations)
            - Combinatorics (e.g., counting principles, probability)
            - Optimization (e.g., finding maxima/minima)
            
            Identify key components, constraints, and relationships. Provide a structured summary.""",
            context=""
        )

        # Phase 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Attempt an algebraic solution. Show all steps and transformations.",
                context=analysis
            ),
            self.generate(
                instruction="Attempt a geometric interpretation. Use diagrams and visual reasoning if applicable.",
                context=analysis
            ),
            self.generate(
                instruction="Attempt a combinatorial argument. Focus on counting principles and logical reasoning.",
                context=analysis
            ),
            self.generate(
                instruction="Attempt an optimization approach. Look for maxima/minima or extremal conditions.",
                context=analysis
            )
        )

        # Phase 3: Iterative Refinement and Validation
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Critique and refine this solution. Correct errors, add missing details, and ensure logical consistency.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Phase 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Evaluate all refined solutions. Select the most robust and accurate approach.
            Consider clarity, completeness, and adherence to problem constraints. Synthesize into a final answer.""",
            contexts_list=refined_strategies
        )

        # Phase 5: Final Verification and Output
        verification = await self.revise(
            instruction="Verify the final solution against the original problem. Ensure all constraints are satisfied and the answer is an integer between 000 and 999.",
            context=final_solution
        )

        return verification