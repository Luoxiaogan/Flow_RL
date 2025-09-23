# Workflow ID: gsm8k_6_0
# Benchmark: gsm8k
# Data Indices: [31, 7]

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

        # Step 1: Initial Analysis - Extract key information
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, relationships, and constraints:
            - Identify all numbers and their units
            - List entities (people, objects, etc.)
            - Describe relationships (e.g., 'three times more')
            - Highlight constraints (e.g., totals, remainders)
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Problem Classification - Determine problem type
        classification = await self.generate(
            instruction=f"""Classify the problem based on the extracted information:
            {initial_analysis}
            
            Categories:
            - Sequential operations (step-by-step calculations)
            - Rate problems (distance/speed/time, work rates)
            - Proportions (percentages, fractions, scaling)
            - Distributions (dividing quantities, equal sharing)
            
            Provide a clear classification and justification.""",
            context=initial_analysis
        )

        # Step 3: Solution Strategy Generation - Outline solution steps
        strategy = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Generate a step-by-step solution strategy:
            - List all required calculations
            - Specify the order of operations
            - Highlight intermediate results to track""",
            context=classification
        )

        # Step 4: Calculation Execution - Perform calculations with validation
        steps = strategy.split("\n")  # Split strategy into individual steps
        results = []
        for i, step in enumerate(steps):
            if step.strip():  # Skip empty lines
                calculation = await self.generate(
                    instruction=f"""Perform the following calculation:
                    {step}
                    
                    Show all intermediate results and units.""",
                    context="\n".join(results)  # Pass previous results as context
                )
                validated = await self.revise(
                    instruction=f"""Validate the calculation:
                    {calculation}
                    
                    Check for errors and ensure correctness.""",
                    context=calculation
                )
                results.append(validated)

        # Step 5: Final Answer Extraction - Summarize to extract the final value
        final_answer = await self.summarize(
            instruction="""Condense the solution process to extract the final numerical answer:
            - Isolate the final value
            - Ensure the answer is numerically exact""",
            context="\n".join(results)
        )

        return final_answer