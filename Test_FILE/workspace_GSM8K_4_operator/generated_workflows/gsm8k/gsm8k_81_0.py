# Workflow ID: gsm8k_81_0
# Benchmark: gsm8k
# Data Indices: [26, 76]

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
            instruction="""Identify all numerical values, their context, and relationships. 
            Plan the sequence of operations needed to solve the problem. Format the plan as a step-by-step outline.""",
            context=""
        )

        # Step 2: Execute Planned Steps
        steps = initial_analysis.split('\n')
        intermediate_results = []
        current_context = ""

        for step in steps:
            if not step.strip():
                continue

            execution = await self.generate(
                instruction=f"Perform the following step: {step}. Track intermediate results explicitly.",
                context=current_context
            )
            intermediate_results.append(execution)
            current_context = execution

        # Step 3: Validate Intermediate Results
        validation_tasks = [
            self.revise(
                instruction="Check the calculations for accuracy. Correct any errors and clarify the reasoning.",
                context=result
            ) for result in intermediate_results
        ]
        validated_results = await asyncio.gather(*validation_tasks)

        # Step 4: Final Synthesis
        final_answer = await self.ensemble(
            instruction="Synthesize all solution paths into a unified answer. Ensure the final result is numerically exact.",
            contexts_list=validated_results
        )

        return final_answer