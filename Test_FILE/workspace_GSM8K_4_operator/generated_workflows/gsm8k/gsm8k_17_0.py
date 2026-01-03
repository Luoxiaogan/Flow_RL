# Workflow ID: gsm8k_17_0
# Benchmark: gsm8k
# Data Indices: [54, 233]

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
            instruction="""Extract all numerical values, their units, and relationships:
            - List all numbers and what they represent
            - Identify relationships between numbers (e.g., addition, multiplication)
            - Note any constraints or conditions""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the extracted information:
                {extraction}
                
                Develop a solution strategy focusing on sequential operations.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Using the extracted information:
                {extraction}
                
                Develop a solution strategy focusing on proportional reasoning.""",
                context=extraction
            ),
            self.generate(
                instruction=f"""Using the extracted information:
                {extraction}
                
                Develop a solution strategy focusing on distribution and sharing.""",
                context=extraction
            )
        )

        # Step 3: Validate and refine each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate and refine this strategy:
                - Check all calculations for accuracy
                - Ensure units are consistent
                - Suggest corrections if errors are found""",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the refined strategies:
            - Compare accuracy and clarity
            - Select the most robust and well-reasoned approach""",
            contexts_list=refined_strategies
        )

        # Step 5: Summarize the final answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_solution
        )

        return final_answer.strip()