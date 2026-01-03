# Workflow ID: gsm8k_102_0
# Benchmark: gsm8k
# Data Indices: [122, 252]

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

        # Step 1: Dynamic Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Extract all numerical values and their units.
            - Identify relationships between entities.
            - Classify the problem type (sequential, rate, proportion, etc.).
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct calculations:
                {analysis}
                Perform step-by-step arithmetic operations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using proportional relationships:
                {analysis}
                Scale ratios or percentages as needed.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using unit conversions or rates:
                {analysis}
                Handle speed, time, distance, or other rate-based calculations.""",
                context=analysis
            )
        )

        # Step 3: Synthesize Best Solution Path
        synthesis = await self.ensemble(
            instruction="Select the most complete and accurate solution path.",
            contexts_list=paths
        )

        # Step 4: Iterative Refinement
        refined_solution = synthesis
        for _ in range(3):  # Limit iterations to avoid infinite loops
            validation = await self.generate(
                instruction=f"Validate and improve clarity of the solution: {refined_solution}",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"Correct issues identified: {validation}",
                    context=refined_solution
                )
            else:
                break

        # Step 5: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer with full precision.",
            context=refined_solution
        )

        return final_answer