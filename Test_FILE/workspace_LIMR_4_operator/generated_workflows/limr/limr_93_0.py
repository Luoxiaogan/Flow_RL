# Workflow ID: limr_93_0
# Benchmark: limr
# Data Indices: [131, 198]

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

        # Step 1: Initial Analysis - Decompose the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the problem type (e.g., geometry, number theory, combinatorics).
            - Extract key components (e.g., variables, equations, constraints).
            - Highlight any ambiguities or missing information.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Based on the analysis: {initial_analysis}, solve using algebraic methods.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Based on the analysis: {initial_analysis}, solve using geometric reasoning.",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Based on the analysis: {initial_analysis}, solve using combinatorial techniques.",
                context=initial_analysis
            )
        )

        # Step 3: Validate and Refine Solutions
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Verify and refine this solution: {strategy}. Ensure all steps are rigorous and correct.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Summarize Key Insights
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction=f"Condense this solution: {solution}. Focus on key steps and results.",
                context=solution
            ) for solution in refined_solutions]
        )

        # Step 5: Ensemble Decision-Making - Choose the best solution
        final_solution = await self.ensemble(
            instruction="""Evaluate the summarized solutions:
            - Select the most rigorous and complete solution.
            - Ensure the final answer is an integer between 000 and 999.
            Provide the chosen solution.""",
            contexts_list=summaries
        )

        # Step 6: Iterative Refinement (Optional)
        for _ in range(2):  # Allow up to 2 refinement iterations
            validation = await self.generate(
                instruction=f"Validate the final solution: {final_solution}. Identify any errors or improvements.",
                context=final_solution
            )
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Fix issues identified: {validation}. Improve the solution.",
                    context=final_solution
                )
            else:
                break

        return final_solution