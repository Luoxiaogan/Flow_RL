# Workflow ID: gsm8k_58_0
# Benchmark: gsm8k
# Data Indices: [66, 72]

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
        
        # Initial Analysis: Extract key information and structure
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, units, and relationships:
            - Identify named entities (people, places, objects)
            - List all numbers with their context
            - Describe relationships and constraints""",
            context=""
        )
        
        # Problem Classification: Determine the type of reasoning required
        classification = await self.generate(
            instruction=f"""Classify the problem based on the following:
            {initial_analysis}
            
            Categories:
            - Rate problems (distance/speed/time, work rates, unit prices)
            - Distribution problems (dividing quantities, equal sharing, remainders)
            - Proportion problems (percentages, fractions, ratios, scaling)
            - Multi-entity problems (tracking different quantities for multiple people/objects)
            - Other (specify)""",
            context=initial_analysis
        )
        
        # Solution Strategy Development: Outline step-by-step solution
        strategy = await self.generate(
            instruction=f"""Develop a step-by-step solution strategy:
            Classification: {classification}
            
            Steps:
            - Define intermediate calculations
            - Specify order of operations
            - Highlight key decision points""",
            context=classification
        )
        
        # Parallel Processing of Steps: Generate and revise potential solutions
        steps = strategy.split('\n')
        potential_solutions = await asyncio.gather(
            *[self.generate(instruction=f"Implement step: {step}", context=strategy) for step in steps]
        )
        revised_solutions = await asyncio.gather(
            *[self.revise(instruction="Validate and refine this step", context=sol) for sol in potential_solutions]
        )
        
        # Ensemble Decision-Making: Select the best approach
        final_solution = await self.ensemble(
            instruction="Evaluate and synthesize the best solution from the refined steps",
            contexts_list=revised_solutions
        )
        
        # Iterative Refinement: Loop to ensure accuracy
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Check for errors and logical inconsistencies in the solution",
                context=final_solution
            )
            if "error" in validation.lower():
                final_solution = await self.revise(
                    instruction=f"Fix identified issues: {validation}",
                    context=final_solution
                )
            else:
                break
        
        # Final Answer Extraction: Summarize to extract the numerical answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the complete solution",
            context=final_solution
        )
        
        return final_answer