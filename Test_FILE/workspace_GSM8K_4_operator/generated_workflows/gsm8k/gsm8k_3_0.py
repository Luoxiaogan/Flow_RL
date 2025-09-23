# Workflow ID: gsm8k_3_0
# Benchmark: gsm8k
# Data Indices: [183, 44]

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
            - Identify all numbers and their units
            - Describe relationships between quantities
            - Classify the problem type (e.g., rate, distribution, proportion)
            - State what the question is asking for
            Provide this information in a structured format.""",
            context=""
        )

        # Step 2: Strategy Generation
        strategy = await self.generate(
            instruction=f"""Based on the following analysis:
            {initial_analysis}
            
            Propose a step-by-step solution strategy:
            - List all intermediate calculations
            - Specify dependencies between steps
            - Include units and expected formats
            Ensure the strategy is complete and logical.""",
            context=initial_analysis
        )

        # Step 3: Parallel Exploration (Optional)
        if "multiple approaches" in strategy.lower():
            approaches = await asyncio.gather(
                self.generate(instruction="Explore first approach...", context=strategy),
                self.generate(instruction="Explore second approach...", context=strategy)
            )
        else:
            approaches = [strategy]

        # Step 4: Validation and Refinement
        refined_solutions = []
        for approach in approaches:
            refined = await self.revise(
                instruction=f"""Validate and refine the following solution:
                {approach}
                
                Check for:
                - Logical consistency
                - Dimensional correctness
                - Arithmetic accuracy
                Correct any errors and improve clarity.""",
                context=approach
            )
            refined_solutions.append(refined)

        # Step 5: Synthesis and Final Output
        final_solution = await self.ensemble(
            instruction="""Synthesize the following solutions into a single coherent answer:
            - Select the most accurate and complete solution
            - Ensure the final answer is a single numerical value
            - Include units if applicable""",
            contexts_list=refined_solutions
        )

        return final_solution