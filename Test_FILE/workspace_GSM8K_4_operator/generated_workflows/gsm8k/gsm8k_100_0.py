# Workflow ID: gsm8k_100_0
# Benchmark: gsm8k
# Data Indices: [11, 255]

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

        # Step 1: Extract key information
        extraction = await self.generate(
            instruction="""Extract all key information from the problem:
            - Identify named entities (people, objects, etc.)
            - List all numerical values and their units/contexts
            - Describe relationships between entities/values
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Classify the problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {extraction}
            
            Possible categories:
            - Sequential operations
            - Rate problems (distance/speed/time, work rates, etc.)
            - Distribution (dividing quantities, sharing, remainders)
            - Proportions (percentages, fractions, ratios, scaling)
            - Multi-entity tracking
            
            Provide a clear classification and reasoning.""",
            context=extraction
        )

        # Step 3: Generate solution steps
        solution_steps = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Generate a step-by-step solution plan:
            - Define intermediate calculations
            - Specify the order of operations
            - Include validation checks for each step""",
            context=classification
        )

        # Step 4: Parallel exploration of solution paths (if applicable)
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using the first approach:
                {solution_steps}""",
                context=solution_steps
            ),
            self.generate(
                instruction=f"""Solve the problem using an alternative approach:
                {solution_steps}""",
                context=solution_steps
            )
        )

        # Step 5: Validate and refine intermediate results
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine the solution:
                Check for logical consistency and numerical accuracy.
                Correct any errors.""",
                context=path
            ) for path in paths]
        )

        # Step 6: Synthesize final result
        final_result = await self.ensemble(
            instruction="""Synthesize the best solution from the refined paths:
            - Ensure numerical accuracy
            - Match the problem's requirements
            - Present the final answer as a single numerical value""",
            contexts_list=refined_paths
        )

        return final_result