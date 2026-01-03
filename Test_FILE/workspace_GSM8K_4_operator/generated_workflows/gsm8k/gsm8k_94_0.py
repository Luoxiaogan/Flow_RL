# Workflow ID: gsm8k_94_0
# Benchmark: gsm8k
# Data Indices: [287, 94]

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

        # Stage 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract key entities, relationships, and classify the problem:
            - Identify all numbers and their contexts.
            - Determine the problem type (rate, distribution, proportion, etc.).
            - Highlight any constraints or conditions.
            Provide a structured summary.""",
            context=""
        )

        # Stage 2: Solution Planning
        plan = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Create a step-by-step plan to solve the problem:
            - List the calculations required.
            - Identify intermediate results to track.
            - Specify the final output format.""",
            context=analysis
        )

        # Stage 3: Parallel Execution of Steps
        steps = await asyncio.gather(
            *[self.generate(
                instruction=f"Perform step: {step}",
                context=plan
            ) for step in plan.split('\n') if "Calculate" in step]
        )

        # Stage 4: Intermediate Validation
        validated_steps = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine this calculation if necessary.",
                context=step
            ) for step in steps]
        )

        # Stage 5: Final Synthesis
        final_answer = await self.ensemble(
            instruction="Combine all validated results into a single numerical answer.",
            contexts_list=validated_steps
        )

        return final_answer