# Workflow ID: gsm8k_69_0
# Benchmark: gsm8k
# Data Indices: [236, 278]

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
        analysis = await self.generate(
            instruction="""Extract all numerical values, their context, and relationships:
            - Identify what is being asked
            - List all given numbers and their units
            - Describe the relationships between quantities
            - Classify the problem type (e.g., sequential, rate, distribution)""",
            context=""
        )

        # Step 2: Generate Multiple Solution Paths
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct computation:
                {analysis}
                - Perform calculations step-by-step
                - Show intermediate results
                - Ensure all units are consistent""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Solve using proportional reasoning:
                {analysis}
                - Identify ratios or proportions
                - Scale quantities appropriately
                - Verify consistency with problem constraints""",
                context=analysis
            )
        )

        # Step 3: Validate and Refine Paths
        refined_paths = []
        for path in paths:
            refined = await self.revise(
                instruction="""Validate and refine the solution:
                - Check calculations for errors
                - Ensure logical consistency
                - Improve clarity and presentation""",
                context=path
            )
            refined_paths.append(refined)

        # Step 4: Synthesize Best Solution
        best_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Compare accuracy and clarity
            - Choose the most computationally efficient path
            - Ensure adherence to problem constraints""",
            contexts_list=refined_paths
        )

        # Step 5: Extract Final Answer
        final_answer = await self.summarize(
            instruction="""Condense the solution to extract the final answer:
            - Isolate the numerical result
            - Ensure correct format (integer or decimal)
            - Remove unnecessary details""",
            context=best_solution
        )

        return final_answer