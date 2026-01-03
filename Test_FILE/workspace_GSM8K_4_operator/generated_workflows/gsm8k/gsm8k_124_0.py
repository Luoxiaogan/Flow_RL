# Workflow ID: gsm8k_124_0
# Benchmark: gsm8k
# Data Indices: [129, 143]

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
            instruction="""Extract all numerical values, entities, and relationships from the problem. 
            Identify the problem type (e.g., rate, distribution, proportion). 
            Provide a structured breakdown of the problem components.""",
            context=""
        )

        # Step 2: Problem Type Classification
        classification = await self.generate(
            instruction=f"""Based on the following analysis:
            {initial_analysis}
            
            Classify the problem into one of the following categories:
            1. Rate problems (distance/speed/time, work rates, unit prices)
            2. Distribution problems (dividing quantities, equal sharing, remainders)
            3. Proportion problems (percentages, fractions, ratios, scaling)
            4. Multi-entity problems (tracking quantities for multiple people/objects)
            
            Provide a clear classification and reasoning.""",
            context=initial_analysis
        )

        # Step 3: Select Solution Pathway
        if "rate" in classification.lower():
            solution_strategy = "Use proportional reasoning to calculate rates and relationships."
        elif "distribution" in classification.lower():
            solution_strategy = "Focus on division and remainders to distribute quantities."
        elif "proportion" in classification.lower():
            solution_strategy = "Apply percentage, fraction, or ratio calculations as needed."
        else:
            solution_strategy = "Use general multi-step reasoning to track quantities for multiple entities."

        solution_pathway = await self.generate(
            instruction=f"""Based on the classification:
            {classification}
            
            Develop a step-by-step solution strategy:
            {solution_strategy}
            
            Ensure each step builds on the previous one and produces intermediate results.""",
            context=classification
        )

        # Step 4: Iterative Solution Construction
        steps = solution_pathway.split("\n")
        intermediate_results = []
        for step in steps:
            if step.strip():  # Skip empty lines
                result = await self.generate(
                    instruction=f"""Execute the following step:
                    {step}
                    
                    Show all calculations and provide the intermediate result.""",
                    context="\n".join(intermediate_results)
                )
                intermediate_results.append(result)

        # Step 5: Parallel Validation
        parallel_attempts = await asyncio.gather(
            *[self.generate(
                instruction=f"""Re-solve the problem independently using the following strategy:
                {solution_strategy}""",
                context=""
            ) for _ in range(3)]
        )
        validated_solution = await self.ensemble(
            instruction="Compare the following solutions and select the most accurate one:",
            contexts_list=parallel_attempts
        )

        # Step 6: Final Answer Extraction
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the validated solution.",
            context=validated_solution
        )

        return final_answer.strip()