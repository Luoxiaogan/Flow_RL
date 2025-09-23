# Workflow ID: limr_47_0
# Benchmark: limr
# Data Indices: [226, 6]

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

        # Stage 1: Initial Analysis and Classification
        analysis = await self.generate(
            instruction="""Classify the problem and extract key components:
            - Identify all variables, constants, and relationships.
            - Determine the problem type (e.g., algebraic, geometric, probabilistic).
            - List all constraints and boundary conditions.
            Provide a structured analysis.""",
            context=""
        )

        # Stage 2: Parallel Exploration of Solution Approaches
        approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Using algebraic reasoning:
                - Perform symbolic manipulation.
                - Solve equations or simplify expressions.
                - Highlight key insights.
                Problem context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using geometric reasoning:
                - Analyze spatial relationships.
                - Use coordinate geometry or vector algebra.
                - Highlight key insights.
                Problem context: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using combinatorial reasoning:
                - Enumerate possibilities.
                - Apply counting principles or probability rules.
                - Highlight key insights.
                Problem context: {analysis}""",
                context=analysis
            )
        )

        # Stage 3: Ensemble to Select Best Approach
        best_approach = await self.ensemble(
            instruction="""Compare the approaches and select the most promising:
            - Evaluate completeness and correctness.
            - Consider computational feasibility.
            - Choose the approach with the clearest path to solution.""",
            contexts_list=approaches
        )

        # Stage 4: Iterative Refinement
        refined_solution = best_approach
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.revise(
                instruction=f"""Verify the solution:
                - Check all calculations and logical steps.
                - Identify any errors or gaps.
                Solution context: {refined_solution}""",
                context=refined_solution
            )
            if "error" in validation.lower() or "gap" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Address issues identified in validation:
                    - Fix errors or fill gaps.
                    - Maintain precision and clarity.
                    Validation context: {validation}""",
                    context=refined_solution
                )
            else:
                break

        # Stage 5: Final Synthesis and Output
        final_answer = await self.summarize(
            instruction="""Condense the solution into a concise answer:
            - Include only essential steps and insights.
            - Format the result as an integer between 000 and 999.""",
            context=refined_solution
        )

        return final_answer