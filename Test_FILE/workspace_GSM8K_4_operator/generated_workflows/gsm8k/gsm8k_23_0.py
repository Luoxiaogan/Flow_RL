# Workflow ID: gsm8k_23_0
# Benchmark: gsm8k
# Data Indices: [131, 92]

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

        # Step 1: Problem Analysis and Classification
        analysis = await self.generate(
            instruction="""Analyze the problem structure and classify it:
            - Identify key entities, numbers, and relationships.
            - Determine the type of problem (rate, proportion, distribution, etc.).
            - Highlight constraints and what is being asked.
            Provide structured output.""",
            context=""
        )

        # Step 2: Generate Solution Strategy
        strategy = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Develop a step-by-step solution strategy:
            - Outline the sequence of operations required.
            - Specify intermediate goals and how they contribute to the final answer.
            - Consider potential pitfalls and how to address them.""",
            context=analysis
        )

        # Step 3: Parallel Exploration of Sub-Problems
        sub_problems = await self.generate(
            instruction=f"""From the strategy:
            {strategy}
            
            Identify independent sub-problems that can be solved in parallel.
            For each sub-problem, describe the required calculations and context.""",
            context=strategy
        )
        sub_problem_tasks = [
            self.generate(
                instruction=f"Solve this sub-problem: {sub_problem}",
                context=sub_problems
            ) for sub_problem in sub_problems.split("\n") if sub_problem.strip()
        ]
        sub_problem_results = await asyncio.gather(*sub_problem_tasks)

        # Step 4: Iterative Refinement
        refined_results = []
        for result in sub_problem_results:
            refined = await self.revise(
                instruction="Validate and refine this result. Ensure calculations are correct and context is preserved.",
                context=result
            )
            refined_results.append(refined)

        # Step 5: Final Synthesis and Validation
        synthesis = await self.ensemble(
            instruction="""Synthesize all refined results into a coherent solution:
            - Combine intermediate results logically.
            - Ensure numerical accuracy and consistency.
            - Present the final answer in the required format.""",
            contexts_list=refined_results
        )

        # Return the final answer
        return synthesis