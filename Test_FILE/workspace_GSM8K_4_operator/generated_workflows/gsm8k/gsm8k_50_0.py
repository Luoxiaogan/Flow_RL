# Workflow ID: gsm8k_50_0
# Benchmark: gsm8k
# Data Indices: [193, 250]

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
        import re

        # Step 1: Extract numerical values, units, and relationships
        extraction = await self.generate(
            instruction="""Extract all numerical values, units, and relationships from the problem. 
            Classify the problem type (e.g., sequential operations, rate problems, distribution, proportions). 
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Identify the sequence of operations
        operation_sequence = await self.generate(
            instruction=f"""Based on the extracted information: {extraction}
            Identify the sequence of operations needed to solve the problem. 
            Include intermediate steps and specify the order of calculations.""",
            context=extraction
        )

        # Step 3: Perform intermediate calculations
        steps = re.split(r'\n\d+\.', operation_sequence)[1:]  # Split into individual steps
        intermediate_results = []
        for i, step in enumerate(steps):
            calculation = await self.generate(
                instruction=f"""Perform the following calculation: {step}
                Show all steps and intermediate results. Ensure numerical precision.""",
                context="\n".join(intermediate_results)
            )
            # Validate the calculation
            validation = await self.revise(
                instruction=f"""Validate the calculation: {calculation}
                Check for arithmetic errors and logical consistency.""",
                context=calculation
            )
            if "error" in validation.lower():
                calculation = await self.revise(
                    instruction=f"""Fix the following issues: {validation}""",
                    context=calculation
                )
            intermediate_results.append(calculation)

        # Step 4: Explore alternative solution paths (if applicable)
        alternatives = await asyncio.gather(
            self.generate(instruction="Solve using an alternative method (e.g., fractions instead of percentages).", context=""),
            self.generate(instruction="Solve using a different sequence of operations.", context="")
        )
        # Synthesize the best result
        final_solution = await self.ensemble(
            instruction="Select the most accurate and efficient solution.",
            contexts_list=[*intermediate_results, *alternatives]
        )

        # Step 5: Summarize the final answer
        summary = await self.summarize(
            instruction="Extract the final numerical answer from the solution. Ensure it is exact and properly formatted.",
            context=final_solution
        )

        return summary.strip()