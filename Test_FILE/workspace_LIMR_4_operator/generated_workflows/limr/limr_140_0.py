# Workflow ID: limr_140_0
# Benchmark: limr
# Data Indices: [267, 219]

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

        # Phase 1: Problem Analysis and Strategy Generation
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the domain (geometry, number theory, etc.)
            - Extract key numbers, variables, and relationships
            - Classify the problem type (e.g., modular arithmetic, probability)
            - Suggest potential solution strategies
            Provide structured output.""",
            context=""
        )

        # Phase 2: Parallel Exploration of Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Attempt solution using direct computation:
                {analysis}
                Show all steps explicitly.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Attempt solution using pattern recognition:
                {analysis}
                Look for recurring structures or symmetries.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Attempt solution using theoretical insights:
                {analysis}
                Apply relevant theorems or principles.""",
                context=analysis
            )
        )

        # Phase 3: Evaluate and Select Best Path
        best_path = await self.ensemble(
            instruction="""Evaluate the following solution attempts:
            - Assess correctness and completeness
            - Check for logical consistency
            - Prefer elegant and efficient solutions
            Select the best approach or synthesize insights.""",
            contexts_list=paths
        )

        # Phase 4: Iterative Refinement
        refined_solution = best_path
        for _ in range(3):  # Allow up to 3 refinement iterations
            critique = await self.generate(
                instruction=f"""Critique the current solution:
                {refined_solution}
                Identify errors, gaps, or areas for improvement.""",
                context=refined_solution
            )
            if "error" in critique.lower() or "gap" in critique.lower():
                refined_solution = await self.revise(
                    instruction=f"""Improve the solution based on critique:
                    {critique}""",
                    context=refined_solution
                )
            else:
                break

        # Phase 5: Final Synthesis and Output
        final_answer = await self.summarize(
            instruction=f"""Condense the refined solution into a concise answer:
            {refined_solution}
            Ensure clarity and precision. Present the final result as an integer between 000 and 999.""",
            context=refined_solution
        )

        return final_answer