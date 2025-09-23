# Workflow ID: gsm8k_84_0
# Benchmark: gsm8k
# Data Indices: [253, 67]

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
        import re

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Extract all numerical values and their context (units, relationships).
            - Classify the problem type (sequential, rate, distribution, proportional).
            - Identify constraints and expected answer format.
            Provide a structured summary.""",
            context=""
        )

        # Phase 2: Parallel Exploration
        direct_calculation = await self.generate(
            instruction=f"""Solve using direct arithmetic operations:
            - Perform step-by-step calculations based on extracted values.
            - Show intermediate results and their context.
            Analysis: {analysis}""",
            context=analysis
        )

        proportional_reasoning = await self.generate(
            instruction=f"""Solve using proportional reasoning:
            - Handle ratios, percentages, or scaling.
            - Show intermediate steps and their logic.
            Analysis: {analysis}""",
            context=analysis
        )

        rate_based_reasoning = await self.generate(
            instruction=f"""Solve using rate-based reasoning:
            - Handle distance/speed/time or work-rate problems.
            - Show intermediate steps and their logic.
            Analysis: {analysis}""",
            context=analysis
        )

        # Select the best approach
        best_solution = await self.ensemble(
            instruction="""Compare solution attempts:
            - Evaluate completeness, accuracy, and alignment with problem constraints.
            - Select the most promising approach.""",
            contexts_list=[direct_calculation, proportional_reasoning, rate_based_reasoning]
        )

        # Phase 3: Iterative Validation
        refined_solution = best_solution
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction=f"""Validate the solution:
                - Check intermediate results for consistency.
                - Identify and correct errors.
                Current solution: {refined_solution}""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Refine the solution:
                    - Address identified issues: {validation}.
                    - Ensure all steps are accurate and complete.""",
                    context=refined_solution
                )
            else:
                break

        # Phase 4: Final Synthesis
        final_answer = await self.summarize(
            instruction="""Condense the solution:
            - Include key steps and intermediate results.
            - Present the final numerical answer in the required format.""",
            context=refined_solution
        )

        return final_answer