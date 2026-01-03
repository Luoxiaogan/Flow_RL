# Workflow ID: gsm8k_15_0
# Benchmark: gsm8k
# Data Indices: [40, 70]

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

        # Step 1: Analyze the problem structure
        analysis = await self.generate(
            instruction="""Analyze the problem to extract:
            - Key numbers and their units
            - Relationships between quantities
            - Problem type (rate, proportion, distribution, etc.)
            - What the question asks for
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Determine the solution strategy
        strategy = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Select the most appropriate solution strategy:
            - Sequential Operations: Step-by-step calculations
            - Rate Problems: Speed, time, or work rates
            - Proportions: Percentages, ratios, scaling
            - Multi-entity Tracking: Multiple actors or objects
            Explain the chosen strategy and why it fits.""",
            context=analysis
        )

        # Step 3: Generate multiple solution attempts in parallel
        solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using the sequential operations strategy:
                {strategy}
                
                Show all steps and intermediate results.""",
                context=strategy
            ),
            self.generate(
                instruction=f"""Solve the problem using the rate problems strategy:
                {strategy}
                
                Focus on rates, times, and relationships.""",
                context=strategy
            ),
            self.generate(
                instruction=f"""Solve the problem using the proportions strategy:
                {strategy}
                
                Emphasize percentages, ratios, and scaling.""",
                context=strategy
            )
        )

        # Step 4: Synthesize the best solution
        best_solution = await self.ensemble(
            instruction="""Evaluate the solutions and select the best one:
            - Accuracy of calculations
            - Logical consistency
            - Completeness of reasoning
            Provide the final answer.""",
            contexts_list=solutions
        )

        # Step 5: Validate and refine the solution
        validation = await self.generate(
            instruction=f"""Validate the solution:
            {best_solution}
            
            Check for:
            - Numerical accuracy
            - Logical consistency
            - Alignment with the problem requirements""",
            context=best_solution
        )

        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Revise the solution to fix identified issues:
                {validation}""",
                context=best_solution
            )
            return refined_solution
        else:
            return best_solution