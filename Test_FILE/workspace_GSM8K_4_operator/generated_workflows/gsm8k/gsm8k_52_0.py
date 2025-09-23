# Workflow ID: gsm8k_52_0
# Benchmark: gsm8k
# Data Indices: [181, 1]

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

        # Step 1: Initial Analysis - Extract key information and propose solution steps
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem. 
            Identify what is being asked and propose a sequence of steps to solve it. 
            Format the output as a structured plan with clear intermediate goals.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction="""Solve the problem using a direct sequential approach. 
                Show all intermediate calculations and maintain numerical precision.""",
                context=initial_analysis
            ),
            self.generate(
                instruction="""Solve the problem by breaking it into smaller sub-problems. 
                Address each sub-problem independently and combine the results.""",
                context=initial_analysis
            ),
            self.generate(
                instruction="""Solve the problem using proportional reasoning. 
                Identify scaling factors, percentages, or ratios and apply them systematically.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Validate each solution path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate this solution path: {path}. 
                Check for calculation errors, unit mismatches, and logical inconsistencies. 
                Refine the solution if necessary.""",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Synthesis - Select or merge the best solution
        final_solution = await self.ensemble(
            instruction="""Compare the refined solution paths and select the most accurate and complete one. 
            If multiple paths are equally valid, merge them into a unified solution.""",
            contexts_list=refined_paths
        )

        # Step 5: Final Output - Summarize the result
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer from the solution. 
            Ensure it is presented in the required format with appropriate units.""",
            context=final_solution
        )

        return final_answer