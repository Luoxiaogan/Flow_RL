# Workflow ID: limr_98_0
# Benchmark: limr
# Data Indices: [231, 291]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify key entities, numbers, and relationships.
            - Classify the problem type (geometry, algebra, combinatorics, etc.).
            - Highlight constraints and conditions.
            - Define the solution space and applicable methods.
            Provide structured output.""",
            context=""
        )
        summary = await self.summarize(
            instruction="Condense the analysis into key points and actionable insights.",
            context=analysis
        )

        # Phase 2: Parallel Solution Exploration
        strategies = [
            "Algebraic manipulation and equation solving.",
            "Geometric reasoning and visualization.",
            "Combinatorial counting and probability analysis.",
            "Number theory techniques like modular arithmetic."
        ]
        solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve the problem using {strategy}. Show all steps and reasoning.",
                context=summary
            ) for strategy in strategies]
        )

        # Phase 3: Validation and Refinement
        refined_solutions = []
        for solution in solutions:
            validation = await self.generate(
                instruction="Validate this solution against the problem constraints and conditions.",
                context=solution
            )
            if "error" in validation.lower() or "inconsistent" in validation.lower():
                refined = await self.revise(
                    instruction="Refine the solution to address identified issues.",
                    context=solution
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(solution)

        # Phase 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best insights from all solutions:
            - Select the most rigorous and precise solution.
            - Ensure the final answer is an integer between 000 and 999.
            - Provide justification for the chosen solution.""",
            contexts_list=refined_solutions
        )

        return final_solution