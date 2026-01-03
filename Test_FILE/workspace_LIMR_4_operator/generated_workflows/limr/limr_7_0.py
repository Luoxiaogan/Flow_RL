# Workflow ID: limr_7_0
# Benchmark: limr
# Data Indices: [295, 173]

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

        # Step 1: Hierarchical Decomposition
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the problem type (geometry, number theory, etc.)
            - Extract key components (variables, constraints, relationships)
            - Highlight any special conditions or requirements""",
            context=""
        )
        refined_analysis = await self.revise(
            instruction="Ensure completeness and accuracy of the analysis",
            context=analysis
        )

        # Step 2: Parallel Exploration
        strategies = ["algebraic manipulation", "geometric transformations", "combinatorial arguments"]
        candidate_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"Attempt solution using {strategy}",
                context=refined_analysis
            ) for strategy in strategies]
        )

        # Step 3: Iterative Refinement
        refined_solutions = []
        for solution in candidate_solutions:
            validation = await self.generate(
                instruction="Validate the solution for correctness and completeness",
                context=solution
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=solution
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(solution)

        # Step 4: Synthesis and Finalization
        final_solution = await self.ensemble(
            instruction="Synthesize refined solutions into a coherent final answer",
            contexts_list=refined_solutions
        )
        formatted_answer = await self.summarize(
            instruction="Condense the final solution into a concise format with an exact integer answer",
            context=final_solution
        )

        return formatted_answer