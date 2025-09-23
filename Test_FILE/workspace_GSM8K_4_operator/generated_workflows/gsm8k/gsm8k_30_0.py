# Workflow ID: gsm8k_30_0
# Benchmark: gsm8k
# Data Indices: [120, 114]

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

        # Step 1: Extract key information and classify problem type
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, units, relationships, and constraints from the problem. 
            Classify the problem type (e.g., sequential operations, rate problems, proportions). 
            Identify what the question is asking for.""",
            context=""
        )

        # Step 2: Determine solution strategy based on problem type
        strategy = await self.generate(
            instruction=f"""Based on the analysis: {initial_analysis}
            Identify the solution strategy:
            - For sequential operations, outline the calculation steps.
            - For rate problems, identify distance, speed, and time relationships.
            - For proportions, determine scaling factors or percentages.
            Provide a detailed plan for solving the problem.""",
            context=initial_analysis
        )

        # Step 3: Execute sequential calculations
        steps = strategy.split("\n")  # Split strategy into individual steps
        intermediate_results = []
        for i, step in enumerate(steps):
            result = await self.generate(
                instruction=f"""Perform the following step: {step}
                Show all calculations and document intermediate results.""",
                context="\n".join(intermediate_results)  # Accumulate context from previous steps
            )
            intermediate_results.append(result)

        # Step 4: Validate and revise intermediate results
        validation_tasks = [
            self.revise(
                instruction=f"""Validate the following result: {result}
                Check for accuracy, consistency, and alignment with the problem's constraints.
                Suggest corrections if necessary.""",
                context=result
            )
            for result in intermediate_results
        ]
        validated_results = await asyncio.gather(*validation_tasks)

        # Apply corrections if needed
        corrected_results = []
        for original, validated in zip(intermediate_results, validated_results):
            if "error" in validated.lower():
                corrected = await self.revise(
                    instruction=f"""Revise the following result based on validation feedback: {validated}""",
                    context=original
                )
                corrected_results.append(corrected)
            else:
                corrected_results.append(original)

        # Step 5: Extract final answer
        final_answer = await self.summarize(
            instruction="""From the corrected results, extract the final numerical answer. 
            Ensure the output is a single numerical value.""",
            context="\n".join(corrected_results)
        )

        return final_answer.strip()