# Workflow ID: limr_146_0
# Benchmark: limr
# Data Indices: [118, 136]

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

        # Initial Analysis
        analysis = await self.generate(
            instruction="""Extract key components:
            - Variables and constants
            - Constraints and relationships
            - Problem type (algebraic, geometric, etc.)
            - Potential solution strategies
            Organize findings systematically.""",
            context=""
        )

        # Parallel Exploration
        strategies = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Generate multiple solution strategies:
            - Strategy 1: Algebraic manipulation
            - Strategy 2: Geometric interpretation
            - Strategy 3: Combinatorial reasoning
            - Strategy 4: Number-theoretic approach
            Provide detailed outlines for each.""",
            context=analysis
        )

        strategy_list = strategies.split("\n\n")  # Assume strategies are separated by double newlines
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine and validate this strategy:\n{strategy}",
                context=analysis
            ) for strategy in strategy_list]
        )

        # Synthesis and Validation
        synthesis = await self.ensemble(
            instruction="""Compare and synthesize refined solutions:
            - Select most rigorous and complete approach
            - Resolve conflicts between strategies
            - Ensure final solution meets all constraints""",
            contexts_list=refined_solutions
        )

        # Iterative Refinement
        final_solution = synthesis
        for _ in range(3):  # Allow up to 3 refinement cycles
            validation = await self.generate(
                instruction=f"""Validate final solution:
                {final_solution}
                
                Check for:
                - Logical consistency
                - Arithmetic accuracy
                - Compliance with problem constraints""",
                context=analysis
            )
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Fix issues identified in validation:\n{validation}",
                    context=final_solution
                )
            else:
                break

        return final_solution