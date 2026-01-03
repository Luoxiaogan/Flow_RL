# Workflow ID: gsm8k_37_0
# Benchmark: gsm8k
# Data Indices: [79, 272]

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

        # Step 1: Initial Analysis - Extract key information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem. 
            Classify the problem type (e.g., rate, distribution, proportion, multi-entity). 
            Identify what the question asks for and the expected answer format.""",
            context=""
        )

        # Step 2: Solution Planning - Break the problem into sequential steps
        solution_plan = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Plan the solution step-by-step. Include:
            - All required calculations
            - Intermediate results to track
            - Logical flow of operations""",
            context=initial_analysis
        )

        # Step 3: Parallel Execution - Perform independent calculations
        steps = solution_plan.split("\n")
        parallel_results = await asyncio.gather(
            *[self.generate(
                instruction=f"""Perform the following step:
                {step}
                
                Show the calculation and result clearly.""",
                context=solution_plan
            ) for step in steps if step.strip()]
        )

        # Step 4: Validation Loop - Refine and validate intermediate results
        refined_results = []
        for result in parallel_results:
            validated = await self.revise(
                instruction=f"""Validate the following result:
                {result}
                
                Check for:
                - Numerical accuracy
                - Logical consistency
                - Missing details""",
                context=result
            )
            refined_results.append(validated)

        # Step 5: Final Synthesis - Combine results and produce the final answer
        final_answer = await self.ensemble(
            instruction="""Combine all refined results into a single numerical answer. 
            Ensure the answer matches the expected format and is numerically exact.""",
            contexts_list=refined_results
        )

        # Step 6: Summarize Final Output
        summary = await self.summarize(
            instruction="Condense the final answer into a single numerical value.",
            context=final_answer
        )

        return summary.strip()