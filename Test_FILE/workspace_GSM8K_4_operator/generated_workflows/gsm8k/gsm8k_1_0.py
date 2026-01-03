# Workflow ID: gsm8k_1_0
# Benchmark: gsm8k
# Data Indices: [179, 196]

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

        # Step 1: Initial Analysis - Extract key components
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, relationships, and constraints:
            - List all numbers and their contexts (e.g., prices, quantities).
            - Identify what needs to be calculated (e.g., total revenue, total cost).
            - Note any dependencies or conditions (e.g., discounts, unit conversions).""",
            context=""
        )

        # Step 2: Parallel Calculation - Solve independent sub-problems
        sub_problems = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Identify independent sub-problems that can be solved in parallel.
            For each sub-problem, provide a clear calculation plan.""",
            context=initial_analysis
        )

        # Dynamically generate parallel tasks
        tasks = []
        for i, sub_problem in enumerate(sub_problems.split("\n")):
            task = self.generate(
                instruction=f"""Solve the following sub-problem:
                {sub_problem}
                
                Show all steps and intermediate results.""",
                context=initial_analysis
            )
            tasks.append(task)

        parallel_results = await asyncio.gather(*tasks)

        # Step 3: Aggregation and Validation - Combine results and validate
        combined_results = await self.ensemble(
            instruction="""Combine results from all sub-problems:
            - Ensure consistency across calculations.
            - Resolve any conflicts or discrepancies.""",
            contexts_list=parallel_results
        )

        validated_results = await self.revise(
            instruction="""Validate the combined results:
            - Check for logical consistency.
            - Verify numerical accuracy.
            - Identify and correct any errors.""",
            context=combined_results
        )

        # Step 4: Final Calculation and Output - Aggregate and format the answer
        final_result = await self.generate(
            instruction=f"""Using the validated results:
            {validated_results}
            
            Perform the final calculation and format the answer as a single numerical value.""",
            context=validated_results
        )

        # Step 5: Summarize - Condense the solution into a concise output
        summary = await self.summarize(
            instruction="Summarize the solution process and present the final answer.",
            context=final_result
        )

        return summary