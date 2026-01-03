# Workflow ID: gsm8k_64_0
# Benchmark: gsm8k
# Data Indices: [275, 6]

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

        # Step 1: Initial Analysis - Extract key information and plan the solution
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem.
            Identify what is being asked and plan the sequence of operations required to solve it.
            Format the output as a structured breakdown of the problem.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using a direct calculation approach:
                - Follow the sequence of operations identified in the analysis.
                - Show all intermediate steps and results.
                - Ensure precision in calculations.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using a step-by-step reasoning approach:
                - Break the problem into smaller sub-problems.
                - Solve each sub-problem independently.
                - Combine the results to arrive at the final answer.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Validate each path and refine as needed
        validated_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the solution:
                - Check for calculation errors.
                - Ensure all steps are logically consistent.
                - Correct any issues found.""",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Synthesis - Combine the results into a single solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution or synthesize multiple solutions:
            - Compare the results from different paths.
            - Choose the most accurate and complete solution.
            - Ensure the final answer matches the required format.""",
            contexts_list=validated_paths
        )

        # Step 5: Final Output - Return the numerical answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_solution
        )

        return final_answer.strip()