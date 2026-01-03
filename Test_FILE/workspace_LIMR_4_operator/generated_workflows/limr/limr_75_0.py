# Workflow ID: limr_75_0
# Benchmark: limr
# Data Indices: [251, 122]

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
            instruction="""Classify the problem into one of the following categories:
            - Geometry
            - Number Theory
            - Algebra
            - Combinatorics
            - Probability
            
            Identify key components such as variables, constraints, relationships, and expected answer format.
            Provide structured output.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        sub_problems = await self.generate(
            instruction=f"""Break the problem into sub-problems based on the analysis:
            {initial_analysis}
            
            For each sub-problem, specify:
            - What needs to be solved?
            - Relevant methods or techniques
            - Dependencies on other sub-problems""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration
        sub_problem_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the following sub-problem:
                {sub_problem}
                
                Explore multiple approaches and provide detailed reasoning.""",
                context=sub_problems
            ) for sub_problem in sub_problems.split('\n')]
        )

        # Step 4: Iterative Refinement
        refined_solutions = []
        for solution in sub_problem_solutions:
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {solution}
                
                Check for logical consistency, calculation accuracy, and adherence to constraints.""",
                context=solution
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the solution based on validation feedback:
                    {validation}""",
                    context=solution
                )
                refined_solutions.append(refined)
            else:
                refined_solutions.append(solution)

        # Step 5: Final Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the refined solutions into a coherent final answer.
            Ensure the answer adheres to the required format (integer between 000 and 999).
            Provide a clear explanation of the reasoning process.""",
            contexts_list=refined_solutions
        )

        return final_solution