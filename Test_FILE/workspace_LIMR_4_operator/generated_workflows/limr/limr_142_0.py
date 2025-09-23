# Workflow ID: limr_142_0
# Benchmark: limr
# Data Indices: [138, 158]

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
            instruction="""Analyze the problem thoroughly:
            - Identify the problem type (e.g., algebraic, geometric, combinatorial).
            - Extract key components, variables, and constraints.
            - Highlight any special cases or edge conditions.
            - Suggest potential solution strategies.""",
            context=""
        )

        # Step 2: Parallel Exploration - Explore multiple solution strategies
        strategies = ["algebraic", "geometric", "combinatorial", "numerical"]
        exploration_tasks = [
            self.generate(
                instruction=f"""Solve the problem using a {strategy} approach:
                - Show all steps clearly.
                - Validate intermediate results.
                - Provide the final answer if possible.""",
                context=initial_analysis
            ) for strategy in strategies
        ]
        exploration_results = await asyncio.gather(*exploration_tasks)

        # Step 3: Validation and Refinement - Critique each solution
        refinement_tasks = [
            self.revise(
                instruction=f"""Validate and refine this solution:
                - Check for logical consistency.
                - Correct any errors.
                - Add missing details or clarifications.""",
                context=result
            ) for result in exploration_results
        ]
        refined_results = await asyncio.gather(*refinement_tasks)

        # Step 4: Synthesis and Decision-Making - Choose the best solution
        synthesis = await self.ensemble(
            instruction="""Evaluate all refined solutions:
            - Select the most complete and accurate solution.
            - Combine insights from multiple solutions if beneficial.
            - Ensure the final answer meets problem requirements.""",
            contexts_list=refined_results
        )

        # Step 5: Final Verification - Ensure correctness
        final_verification = await self.revise(
            instruction="""Perform final verification:
            - Double-check all calculations.
            - Validate against edge cases.
            - Confirm the answer format is correct.""",
            context=synthesis
        )

        return final_verification