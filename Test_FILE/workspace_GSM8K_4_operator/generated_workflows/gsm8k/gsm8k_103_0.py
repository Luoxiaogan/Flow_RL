# Workflow ID: gsm8k_103_0
# Benchmark: gsm8k
# Data Indices: [241, 112]

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
        analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Numbers and their context
            - Relationships between quantities
            - Constraints and conditions
            - What is being asked for
            Format as a structured summary.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted information:
                {analysis}
                
                Develop a solution strategy focusing on sequential operations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the extracted information:
                {analysis}
                
                Develop a solution strategy focusing on proportions and scaling.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Using the extracted information:
                {analysis}
                
                Develop a solution strategy focusing on distribution and sharing.""",
                context=analysis
            )
        )

        # Step 3: Validate and Revise Strategies
        validated_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Critique and improve this strategy. Ensure all steps are clear and logical.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Summarize Each Strategy
        summarized_strategies = await asyncio.gather(
            *[self.summarize(
                instruction="Condense this strategy into a concise summary.",
                context=strategy
            ) for strategy in validated_strategies]
        )

        # Step 5: Ensemble the Best Solution
        final_solution = await self.ensemble(
            instruction="Select the most complete and accurate solution. Ensure it addresses all aspects of the problem.",
            contexts_list=summarized_strategies
        )

        # Step 6: Final Validation and Refinement
        refined_solution = await self.revise(
            instruction="Double-check all calculations and ensure the final answer is numerically exact.",
            context=final_solution
        )

        return refined_solution