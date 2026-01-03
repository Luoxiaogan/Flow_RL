# Workflow ID: gsm8k_65_0
# Benchmark: gsm8k
# Data Indices: [291, 87]

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
            instruction="""Extract all key information from the problem:
            - Entities (people, objects, groups)
            - Numbers and their context
            - Relationships and constraints
            - Expected answer format
            Provide structured output.""",
            context=""
        )

        # Step 2: Problem Classification
        classification = await self.generate(
            instruction=f"""Classify the problem based on the analysis:
            {initial_analysis}
            
            Categories:
            - Rate problems (distance/speed/time, work rates)
            - Distribution problems (dividing quantities, remainders)
            - Proportion problems (percentages, fractions, scaling)
            - Sequential operations (step-by-step calculations)
            Identify the type and suggest applicable strategies.""",
            context=initial_analysis
        )

        # Step 3: Parallel Solution Exploration
        strategies = ["Direct computation", "Unit conversion", "Proportional reasoning"]
        solution_paths = await asyncio.gather(
            *[self.generate(
                instruction=f"""Solve the problem using {strategy}:
                {classification}
                
                Show all steps and intermediate results.""",
                context=classification
            ) for strategy in strategies]
        )

        # Step 4: Validation and Refinement
        refined_paths = []
        for path in solution_paths:
            validation = await self.revise(
                instruction=f"""Validate the solution:
                - Check logical consistency
                - Verify numerical accuracy
                - Ensure correct units are used
                Provide detailed feedback.""",
                context=path
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the solution based on feedback:
                    {validation}""",
                    context=path
                )
                refined_paths.append(refined)
            else:
                refined_paths.append(path)

        # Step 5: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Select the most accurate and complete path
            - Merge complementary insights if necessary
            - Ensure the final answer is a single numerical value.""",
            contexts_list=refined_paths
        )

        return final_solution