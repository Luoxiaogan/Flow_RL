# Workflow ID: gsm8k_66_0
# Benchmark: gsm8k
# Data Indices: [109, 99]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio

        # Step 1: Initial Analysis - Extract key information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all key entities, numbers, and relationships from the problem. 
            Classify the problem into one of the following categories:
            - Sequential Operations
            - Rate Problems (distance/speed/time, work rates, unit prices)
            - Distribution (dividing quantities, equal sharing, remainders)
            - Proportions (percentages, fractions, ratios, scaling)
            - Multi-entity (tracking different quantities for multiple people/objects)
            Provide structured output with clear labels.""",
            context=""
        )

        # Step 2: Parallel Solution Attempts - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted information: {initial_analysis}
                Solve the problem using algebraic reasoning. Show all steps and intermediate results.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the extracted information: {initial_analysis}
                Solve the problem using logical reasoning. Focus on relationships and constraints.""",
                context=initial_analysis
            )
        )

        # Step 3: Refinement and Validation - Improve clarity and validate solutions
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Improve clarity, correct errors, and add missing details. 
                Validate the solution against the problem statement.""",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Synthesis - Select the best solution
        final_solution = await self.ensemble(
            instruction="""Compare the refined solutions and select the best one based on:
            - Correctness of calculations
            - Clarity of reasoning
            - Alignment with problem requirements""",
            contexts_list=refined_solutions
        )

        # Step 5: Extract Final Answer - Summarize to get the numerical result
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution. Ensure it is concise and matches the expected format.",
            context=final_solution
        )

        return final_answer