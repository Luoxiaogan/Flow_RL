# Workflow ID: gsm8k_59_0
# Benchmark: gsm8k
# Data Indices: [202, 265]

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
            instruction="""Extract key information from the problem:
            - Identify all numerical values and their units.
            - Classify the problem type (e.g., sequential operations, rate problem).
            - Determine constraints and relationships between variables.
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Solution Planning
        plan = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Generate a step-by-step plan to solve the problem:
            - Break the problem into smaller sub-problems.
            - Identify the sequence of operations required.
            - Consider alternative approaches and select the most efficient one.""",
            context=analysis
        )

        # Step 3: Execution and Validation
        steps = plan.split("\n")
        results = []
        for step in steps:
            if not step.strip():
                continue
            calculation = await self.generate(
                instruction=f"""Perform the following calculation:
                {step}
                
                Show all intermediate results and units.""",
                context="\n".join(results)
            )
            validation = await self.revise(
                instruction=f"""Validate the calculation:
                {calculation}
                
                Check for errors or inconsistencies.""",
                context=calculation
            )
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the calculation to fix issues:
                    {validation}""",
                    context=calculation
                )
                results.append(refined)
            else:
                results.append(calculation)

        # Step 4: Final Output
        summary = await self.summarize(
            instruction="""Summarize the solution:
            - Include all intermediate results.
            - Highlight the final numerical answer.""",
            context="\n".join(results)
        )

        # Extract the final numerical answer
        final_answer = await self.generate(
            instruction="""Extract the final numerical answer from the summary:
            Return only the numerical value.""",
            context=summary
        )

        return final_answer.strip()