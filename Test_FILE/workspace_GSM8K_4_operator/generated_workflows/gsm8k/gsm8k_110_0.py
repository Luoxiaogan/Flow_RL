# Workflow ID: gsm8k_110_0
# Benchmark: gsm8k
# Data Indices: [149, 174]

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
        analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one of the following categories:
            - Rate Problems (e.g., speed, distance, time)
            - Distribution Problems (e.g., dividing quantities, remainders)
            - Proportional Reasoning (e.g., percentages, ratios, scaling)
            - Multi-entity Tracking (e.g., quantities for multiple people/objects)
            
            Extract key entities, numbers, and relationships. Identify what the question asks for.
            Provide structured output with clear categories and extracted information.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution strategy for rate problems using the analysis:
                {analysis}
                
                Show step-by-step calculations and track intermediate results.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution strategy for distribution problems using the analysis:
                {analysis}
                
                Focus on dividing quantities and handling remainders.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution strategy for proportional reasoning using the analysis:
                {analysis}
                
                Include scaling, percentages, and ratio calculations.""",
                context=analysis
            )
        )

        # Step 3: Execute and Validate Strategies
        validated_strategies = []
        for strategy in strategies:
            execution = await self.generate(
                instruction=f"""Execute the following strategy step-by-step:
                {strategy}
                
                Track intermediate results and validate each step.""",
                context=strategy
            )
            validation = await self.generate(
                instruction=f"""Validate the execution results:
                {execution}
                
                Check for numerical accuracy, logical consistency, and alignment with the problem requirements.""",
                context=execution
            )
            if "error" not in validation.lower():
                validated_strategies.append(execution)

        # Step 4: Ensemble Decision
        final_solution = await self.ensemble(
            instruction="""Select the best solution based on:
            - Numerical accuracy
            - Logical consistency
            - Alignment with problem requirements
            
            Provide the final answer as a single numerical value.""",
            contexts_list=validated_strategies
        )

        # Step 5: Iterative Refinement (if needed)
        refinement_needed = "ambiguous" in final_solution.lower() or "inconsistent" in final_solution.lower()
        while refinement_needed:
            refined_solution = await self.revise(
                instruction=f"""Refine the solution to address ambiguity or inconsistency:
                {final_solution}
                
                Ensure clarity and correctness.""",
                context=final_solution
            )
            final_solution = refined_solution
            refinement_needed = "ambiguous" in final_solution.lower() or "inconsistent" in final_solution.lower()

        return final_solution