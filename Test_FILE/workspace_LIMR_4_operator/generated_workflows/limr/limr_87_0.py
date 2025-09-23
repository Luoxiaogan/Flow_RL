# Workflow ID: limr_87_0
# Benchmark: limr
# Data Indices: [146, 181]

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

        # Step 1: Initial Analysis - Identify Problem Type and Key Components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Classify the problem type (algebra, geometry, number theory, etc.).
            2. Identify key variables, equations, and constraints.
            3. Highlight any special conditions or requirements.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate Multiple Perspectives
        perspectives = await asyncio.gather(
            self.generate(
                instruction="Analyze the problem using algebraic techniques...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Analyze the problem using geometric techniques...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Analyze the problem using combinatorial techniques...",
                context=initial_analysis
            )
        )

        # Step 3: Process Perspectives - Refine and Validate
        processed = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine and validate this perspective: {p}",
                context=p
            ) for p in perspectives]
        )

        # Step 4: Synthesize Perspectives - Build Unified Understanding
        synthesis = await self.ensemble(
            instruction="Synthesize all perspectives into a unified understanding of the problem.",
            contexts_list=processed
        )

        # Step 5: Iterative Refinement - Validate and Improve
        refined_solution = synthesis
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction="Validate the current solution and identify any errors or gaps.",
                context=refined_solution
            )
            if "error" in validation.lower() or "gap" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Address issues identified: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 6: Final Validation - Ensure Precision and Completeness
        final_validation = await self.generate(
            instruction="Perform a final validation of the solution. Ensure all constraints are satisfied and the answer is precise.",
            context=refined_solution
        )

        # Step 7: Extract Final Answer - Present the Result
        final_answer = await self.summarize(
            instruction="Extract the final answer from the solution. Ensure it is an integer between 000 and 999.",
            context=final_validation
        )

        return final_answer