# Workflow ID: gsm8k_74_0
# Benchmark: gsm8k
# Data Indices: [151, 194]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract all numerical values and their context:
            - Identify numbers and their units/labels (e.g., dollars, hours).
            - Classify the problem type (e.g., sequential operations, rate problems).
            - Determine what the question is asking for.
            Format as a structured summary.""",
            context=""
        )

        # Step 2: Solution Planning
        plan = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Create a step-by-step plan to solve the problem:
            - List all calculations needed.
            - Specify the order of operations.
            - Include intermediate results and their context.""",
            context=analysis
        )

        # Step 3: Execution
        execution = await self.generate(
            instruction=f"""Execute the plan:
            Plan:
            {plan}
            
            Perform each calculation step-by-step:
            - Show intermediate results with context.
            - Ensure all steps are numerically correct.""",
            context=plan
        )

        # Step 4: Validation
        validation = await self.revise(
            instruction="""Verify the solution:
            - Check all calculations for numerical accuracy.
            - Ensure intermediate results are consistent.
            - Confirm the final answer matches the expected format.""",
            context=execution
        )

        # Step 5: Final Output
        final_output = await self.summarize(
            instruction="Extract the final numerical answer from the validated solution.",
            context=validation
        )

        return final_output.strip()