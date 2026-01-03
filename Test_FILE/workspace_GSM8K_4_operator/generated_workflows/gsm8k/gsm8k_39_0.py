# Workflow ID: gsm8k_39_0
# Benchmark: gsm8k
# Data Indices: [85, 137]

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

        # Initial analysis to extract key information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and classify its type:
            - Extract all numbers and their context
            - Identify relationships between numbers
            - Determine the question being asked
            - Classify as sequential, rate, distribution, proportion, or multi-entity
            Provide structured analysis.""",
            context=""
        )

        # Conditional branching based on problem type
        if "rate" in initial_analysis.lower():
            solution_strategy = await self.generate(
                instruction=f"""Given the rate problem classification:
                {initial_analysis}
                
                Develop a solution strategy using dimensional analysis:
                - Identify rates and units
                - Set up proportional relationships
                - Perform unit conversions as needed""",
                context=initial_analysis
            )
        elif "distribution" in initial_analysis.lower():
            solution_strategy = await self.generate(
                instruction=f"""Given the distribution problem classification:
                {initial_analysis}
                
                Develop a solution strategy focusing on equal sharing and remainders:
                - Calculate total quantities
                - Divide quantities evenly
                - Handle remainders appropriately""",
                context=initial_analysis
            )
        else:
            solution_strategy = await self.generate(
                instruction=f"""Develop a general solution strategy for:
                {initial_analysis}
                
                Focus on logical sequence of calculations:
                - Define calculation steps
                - Show intermediate results
                - Validate each step""",
                context=initial_analysis
            )

        # Parallel exploration of multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using direct calculations:
                {solution_strategy}""",
                context=solution_strategy
            ),
            self.generate(
                instruction=f"""Solve using estimation techniques:
                {solution_strategy}""",
                context=solution_strategy
            ),
            self.generate(
                instruction=f"""Solve using alternative methods:
                {solution_strategy}""",
                context=solution_strategy
            )
        )

        # Ensemble to synthesize best solution
        synthesized_solution = await self.ensemble(
            instruction="Synthesize the most accurate and efficient solution from the provided paths.",
            contexts_list=solution_paths
        )

        # Iterative refinement to ensure accuracy
        refined_solution = synthesized_solution
        for _ in range(3):  # Limit iterations to prevent infinite loops
            validation = await self.generate(
                instruction=f"""Validate the solution:
                {refined_solution}
                
                Check for:
                - Calculation errors
                - Logical inconsistencies
                - Missing steps""",
                context=refined_solution
            )
            if "error" in validation.lower():
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution to address:
                    {validation}""",
                    context=refined_solution
                )
            else:
                break

        # Final answer extraction
        final_answer = await self.generate(
            instruction=f"""Extract the final numerical answer from:
            {refined_solution}
            
            Ensure the answer is exact and formatted correctly.""",
            context=refined_solution
        )

        return final_answer