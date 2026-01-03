# Workflow ID: gsm8k_55_0
# Benchmark: gsm8k
# Data Indices: [93, 270]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure and classify it:
            - Identify all named entities, numbers, and relationships.
            - Determine the type of problem (rate, proportion, distribution, etc.).
            - Extract constraints and conditions.
            - Assess whether exact calculations or estimations are required.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Solution Exploration
        direct_calculation = self.generate(
            instruction=f"""Solve the problem using direct arithmetic calculations:
            - Perform sequential operations based on the problem structure.
            - Track intermediate results explicitly.
            - Ensure numerical correctness.
            Context: {analysis}""",
            context=analysis
        )
        
        unit_based_reasoning = self.generate(
            instruction=f"""Solve the problem using unit-based reasoning:
            - Track units throughout calculations.
            - Ensure dimensional consistency.
            - Validate intermediate results.
            Context: {analysis}""",
            context=analysis
        )
        
        step_by_step_verification = self.generate(
            instruction=f"""Solve the problem with step-by-step verification:
            - Validate each intermediate result against constraints.
            - Highlight discrepancies and resolve them.
            Context: {analysis}""",
            context=analysis
        )
        
        solutions = await asyncio.gather(direct_calculation, unit_based_reasoning, step_by_step_verification)

        # Step 3: Solution Synthesis
        synthesis = await self.ensemble(
            instruction="""Synthesize the best solution from the provided options:
            - Evaluate numerical correctness.
            - Assess clarity and alignment with the problem context.
            - Resolve discrepancies if necessary.""",
            contexts_list=solutions
        )

        # Step 4: Iterative Refinement
        refined_solution = synthesis
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction=f"""Validate the solution:
                - Check for numerical errors.
                - Ensure alignment with constraints.
                - Flag inconsistencies.
                Solution: {refined_solution}""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution to address issues:
                    - Fix numerical errors.
                    - Clarify reasoning steps.
                    Issues: {validation}""",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Output
        final_answer = await self.summarize(
            instruction="""Condense the solution into a single numerical answer:
            - Preserve intermediate reasoning for verification.
            - Format the final output as a single number.""",
            context=refined_solution
        )

        # Extract the numerical answer using regex
        match = re.search(r'\d+(\.\d+)?', final_answer)
        return float(match.group()) if match else None