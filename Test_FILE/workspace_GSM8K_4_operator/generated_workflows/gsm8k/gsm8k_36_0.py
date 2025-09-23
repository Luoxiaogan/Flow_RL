# Workflow ID: gsm8k_36_0
# Benchmark: gsm8k
# Data Indices: [256, 147]

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
            instruction="""Extract all key components from the problem:
            - Numerical values and their units
            - Relationships between entities
            - What is being asked
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Decompose into sub-problems
        sub_problems = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Decompose the problem into independent sub-problems.
            Each sub-problem should focus on a specific calculation or relationship.
            List them clearly.""",
            context=initial_analysis
        )

        # Step 3: Solve sub-problems in parallel
        sub_problem_results = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve this sub-problem: {sub_problem}",
                context=initial_analysis
            ) for sub_problem in sub_problems.split('\n')]
        )

        # Step 4: Sequential Integration of results
        integrated_result = ""
        for i, result in enumerate(sub_problem_results):
            integrated_result = await self.revise(
                instruction=f"""Integrate this result into the overall solution:
                Previous results: {integrated_result}
                Current result: {result}
                Ensure logical consistency and numerical accuracy.""",
                context=integrated_result
            )

        # Step 5: Final Validation and Synthesis
        final_validation = await self.generate(
            instruction=f"""Validate the integrated result:
            Integrated result: {integrated_result}
            
            Check for:
            - Numerical accuracy
            - Logical consistency
            - Alignment with the original problem statement""",
            context=integrated_result
        )

        # Step 6: Error Handling and Iterative Refinement
        if "error" in final_validation.lower():
            refined_result = await self.revise(
                instruction=f"""Correct errors identified in validation:
                Errors: {final_validation}
                Original result: {integrated_result}""",
                context=integrated_result
            )
            return refined_result.strip()
        else:
            return final_validation.strip()