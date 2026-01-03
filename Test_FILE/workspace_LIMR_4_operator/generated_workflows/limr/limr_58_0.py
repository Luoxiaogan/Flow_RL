# Workflow ID: limr_58_0
# Benchmark: limr
# Data Indices: [46, 65]

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

        # Step 1: Initial Analysis - Classify and decompose the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            1. Identify the domain (geometry, number theory, algebra, etc.)
            2. Extract key variables, constraints, and desired outputs
            3. Suggest potential solution strategies
            Format your response as a structured breakdown.""",
            context=""
        )

        # Step 2: Sub-Problem Decomposition - Break into manageable parts
        sub_problems = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Decompose the problem into sub-problems. For each sub-problem:
            - Define its scope
            - List required inputs and outputs
            - Suggest applicable methods""",
            context=initial_analysis
        )

        # Step 3: Parallel Solution Exploration - Solve sub-problems independently
        sub_problem_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"Solve this sub-problem using appropriate methods: {sub_problem}",
                context=sub_problems
            ) for sub_problem in sub_problems.split("\n\n") if sub_problem.strip()]
        )

        # Step 4: Validation and Refinement - Check correctness and refine
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution: {solution}",
                context=solution
            ) for solution in sub_problem_solutions]
        )

        # Step 5: Synthesis and Final Output - Combine results and select best approach
        final_solution = await self.ensemble(
            instruction="""Synthesize the refined solutions into a cohesive final answer:
            - Ensure all sub-problems are addressed
            - Verify logical consistency
            - Present the final answer in the required format""",
            contexts_list=refined_solutions
        )

        return final_solution