# Workflow ID: limr_26_0
# Benchmark: limr
# Data Indices: [79, 5]

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
            instruction="""Analyze the problem structure:
            - Identify the main mathematical domain (e.g., algebra, geometry, combinatorics).
            - Extract key variables, equations, and constraints.
            - Determine potential solution strategies.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction="Solve using algebraic manipulation and equations.",
                context=analysis
            ),
            self.generate(
                instruction="Solve using geometric reasoning and visualization.",
                context=analysis
            ),
            self.generate(
                instruction="Solve using combinatorial arguments and counting principles.",
                context=analysis
            )
        )

        # Step 3: Validate and Refine Solutions
        refined_paths = []
        for path in paths:
            validation = await self.generate(
                instruction=f"Validate the solution: {path}. Check for logical consistency and precision.",
                context=path
            )
            if "error" in validation.lower():
                revised = await self.revise(
                    instruction=f"Fix issues: {validation}",
                    context=path
                )
                refined_paths.append(revised)
            else:
                refined_paths.append(path)

        # Step 4: Ensemble Best Solution
        best_solution = await self.ensemble(
            instruction="Select the most robust and precise solution. Ensure it meets all constraints.",
            contexts_list=refined_paths
        )

        # Step 5: Final Verification and Formatting
        verification = await self.generate(
            instruction=f"Verify the solution: {best_solution}. Cross-check using alternative methods.",
            context=best_solution
        )
        final_answer = await self.summarize(
            instruction="Extract the final answer as an integer between 000 and 999.",
            context=verification
        )

        return final_answer