# Workflow ID: gsm8k_25_0
# Benchmark: gsm8k
# Data Indices: [29, 219]

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

        # Step 1: Analyze the problem and extract key information
        analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Identify all numbers and their contexts (e.g., units, entities)
            - Determine the question being asked
            - Classify the problem type (e.g., rate, proportion, distribution)
            - Highlight any constraints or conditions""",
            context=""
        )

        # Step 2: Decompose the problem into sub-problems
        decomposition = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Break the problem into smaller steps:
            - List all required calculations
            - Identify dependencies between steps
            - Suggest an order of operations""",
            context=analysis
        )

        # Step 3: Perform calculations in parallel
        steps = decomposition.split("\n")
        calculation_tasks = [
            self.generate(
                instruction=f"""Perform the following calculation:
                {step}
                
                Show all intermediate results and track units.""",
                context=decomposition
            ) for step in steps if step.strip()
        ]
        results = await asyncio.gather(*calculation_tasks)

        # Step 4: Validate intermediate results
        validation = await self.revise(
            instruction="""Check the calculations for correctness:
            - Verify arithmetic operations
            - Ensure units are consistent
            - Confirm all steps contribute to the final answer""",
            context="\n".join(results)
        )

        # Step 5: Combine results into a final answer
        final_answer = await self.ensemble(
            instruction="""Synthesize the validated results into a single numerical answer:
            - Combine intermediate results as needed
            - Ensure the final answer is precise and matches the question's requirements""",
            contexts_list=results
        )

        # Step 6: Summarize the solution
        summary = await self.summarize(
            instruction="Condense the solution into a concise final answer.",
            context=final_answer
        )

        return summary