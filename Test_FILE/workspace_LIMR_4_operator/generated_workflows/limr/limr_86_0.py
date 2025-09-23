# Workflow ID: limr_86_0
# Benchmark: limr
# Data Indices: [26, 186]

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

        # Step 1: Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Identify the problem type (geometry, number theory, etc.)
            - Extract key entities, variables, and constraints
            - Highlight any special conditions or edge cases
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Solve using algebraic methods...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using combinatorial arguments...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using geometric reasoning...",
                context=initial_analysis
            )
        )

        # Step 3: Ensemble to Select Best Approach
        best_approach = await self.ensemble(
            instruction="""Evaluate the provided solutions:
            - Which approach is most rigorous and complete?
            - Which approach aligns best with the problem's constraints?
            Select the optimal solution.""",
            contexts_list=strategies
        )

        # Step 4: Iterative Refinement
        refined_solution = best_approach
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the solution for correctness and completeness...",
                context=refined_solution
            )
            if "error" in validation.lower() or "incomplete" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Address issues: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Synthesis and Answer Extraction
        final_answer = await self.summarize(
            instruction="""Condense the solution into its simplest form:
            - Ensure the final answer is an integer between 000 and 999
            - Remove any unnecessary details""",
            context=refined_solution
        )

        return final_answer