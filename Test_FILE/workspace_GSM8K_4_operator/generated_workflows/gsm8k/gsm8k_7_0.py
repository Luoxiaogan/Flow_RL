# Workflow ID: gsm8k_7_0
# Benchmark: gsm8k
# Data Indices: [139, 117]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.llm)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify key entities (people, objects, quantities).
            - Extract relationships and constraints.
            - Classify the problem type (e.g., sequential operations, rate problems, proportions).
            Provide structured output.""",
            context=""
        )

        # Step 2: Sub-problem Generation
        sub_problems = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Break the problem into sub-problems:
            - Each sub-problem should correspond to a single calculation step.
            - Order sub-problems logically, considering dependencies.
            Provide a numbered list of sub-problems.""",
            context=analysis
        )

        # Step 3: Parallel Solution Generation
        solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve sub-problem {i+1}:
                {sub_problem}
                
                Perform the calculation and provide the result.""",
                context=sub_problem
            ) for i, sub_problem in enumerate(sub_problems.split('\n'))]
        )

        # Step 4: Validation and Refinement
        validated_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the solution for sub-problem {i+1}:
                {solution}
                
                Check for errors and clarify reasoning if needed.""",
                context=solution
            ) for i, solution in enumerate(solutions)]
        )

        # Step 5: Synthesis and Final Answer
        final_answer = await self.ensemble(
            instruction="""Combine the validated solutions into the final answer:
            - Ensure all intermediate results are accounted for.
            - Present the final numerical answer only.""",
            contexts_list=validated_solutions
        )

        return final_answer