# Workflow ID: limr_18_0
# Benchmark: limr
# Data Indices: [271, 126]

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

        # Step 1: Initial Analysis and Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one of the following categories:
            - Geometry (e.g., coordinate geometry, 3D geometry)
            - Number Theory (e.g., modular arithmetic, divisibility)
            - Algebra (e.g., polynomial equations, functional equations)
            - Combinatorics (e.g., counting principles, probability)
            - Optimization (e.g., finding maxima/minima, inequalities)
            Provide a detailed breakdown of the problem's structure and key components.""",
            context=""
        )

        # Step 2: Hierarchical Decomposition
        sub_problems = await self.generate(
            instruction=f"""Based on the classification and analysis:
            {initial_analysis}
            
            Decompose the problem into sub-problems. For each sub-problem:
            - Identify the type (e.g., algebraic manipulation, geometric property)
            - List required inputs and constraints
            - Suggest potential solution methods""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration of Solution Paths
        solution_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the following sub-problem using the suggested method:
                {sub_problem}""",
                context=sub_problems
            ) for sub_problem in sub_problems.split('\n\n')]
        )

        # Step 4: Rigorous Verification and Refinement
        verified_solutions = []
        for path in solution_paths:
            verification = await self.revise(
                instruction=f"""Verify the correctness of the solution:
                {path}
                
                Check for:
                - Logical consistency
                - Mathematical accuracy
                - Adherence to constraints""",
                context=path
            )
            if "error" in verification.lower():
                refined = await self.revise(
                    instruction=f"""Refine the solution to address issues:
                    {verification}""",
                    context=path
                )
                verified_solutions.append(refined)
            else:
                verified_solutions.append(path)

        # Step 5: Synthesis and Final Answer
        final_solution = await self.ensemble(
            instruction="""Synthesize the verified solutions into a unified answer.
            Ensure:
            - All sub-problems are addressed
            - The final answer is an integer between 000 and 999""",
            contexts_list=verified_solutions
        )

        return final_solution