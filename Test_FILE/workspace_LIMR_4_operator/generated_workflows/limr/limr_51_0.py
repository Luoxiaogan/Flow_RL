# Workflow ID: limr_51_0
# Benchmark: limr
# Data Indices: [199, 60]

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

        # Step 1: Initial Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify the problem type (geometry, number theory, etc.)
            - Extract key variables, constants, and constraints
            - Highlight any special conditions or requirements
            - Suggest potential solution strategies""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop an algebraic solution strategy:
                - Outline the steps required
                - Identify intermediate calculations
                - State expected outcomes
                Problem analysis: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a geometric solution strategy:
                - Outline the steps required
                - Identify intermediate constructions
                - State expected outcomes
                Problem analysis: {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a combinatorial solution strategy:
                - Outline the steps required
                - Identify counting principles
                - State expected outcomes
                Problem analysis: {analysis}""",
                context=analysis
            )
        )

        # Step 3: Validate and Refine Strategies
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Critique and refine the following strategy:
                - Check logical consistency
                - Ensure precision and correctness
                - Add missing details if necessary
                Strategy: {strategy}""",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesize and Select Best Strategy
        best_strategy = await self.ensemble(
            instruction="""Compare the refined strategies and select the best one:
            - Evaluate logical soundness
            - Assess completeness and precision
            - Choose the most promising approach""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Solution Verification
        final_solution = await self.generate(
            instruction=f"""Implement the selected strategy:
            - Execute all steps in detail
            - Verify intermediate results
            - Present the final answer with justification
            Selected strategy: {best_strategy}""",
            context=best_strategy
        )

        # Optional: Iterate if errors are detected
        validation = await self.generate(
            instruction=f"""Validate the final solution:
            - Check against problem requirements
            - Ensure all constraints are satisfied
            - Flag any errors or inconsistencies
            Final solution: {final_solution}""",
            context=final_solution
        )

        if "error" in validation.lower():
            final_solution = await self.revise(
                instruction=f"""Revise the solution based on validation feedback:
                - Address flagged issues
                - Recheck all steps
                - Provide corrected solution
                Validation feedback: {validation}""",
                context=final_solution
            )

        return final_solution