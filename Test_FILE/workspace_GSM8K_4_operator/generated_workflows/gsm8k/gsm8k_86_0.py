# Workflow ID: gsm8k_86_0
# Benchmark: gsm8k
# Data Indices: [101, 167]

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

        # Phase 1: Problem Decomposition
        decomposition = await self.generate(
            instruction="""Extract all relevant information from the problem:
            - Identify all numbers and their roles (e.g., principal, rate, time).
            - Highlight relationships between quantities.
            - Clearly state what the question is asking for.
            Format the output as a structured list.""",
            context=""
        )

        # Phase 2: Solution Strategy Generation
        strategy = await self.generate(
            instruction=f"""Based on the decomposition:
            {decomposition}
            
            Generate a step-by-step solution strategy:
            - List all required calculations in order.
            - Specify intermediate results and their dependencies.
            - Ensure numerical precision and unit consistency.""",
            context=decomposition
        )

        # Phase 3: Parallel Computation
        steps = strategy.split("\n")
        calculations = await asyncio.gather(
            *[self.generate(
                instruction=f"""Perform the following calculation:
                {step}
                
                Show the result with appropriate units.""",
                context=decomposition
            ) for step in steps if step.strip()]
        )

        # Phase 4: Validation and Refinement
        validated_results = await asyncio.gather(
            *[self.revise(
                instruction=f"""Validate the following calculation:
                {calc}
                
                Check for numerical accuracy and unit consistency.""",
                context=calc
            ) for calc in calculations]
        )

        # Phase 5: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer from the validated results.
            Ensure the output is a single number with no additional text.""",
            context="\n".join(validated_results)
        )

        return final_answer