# Workflow ID: gsm8k_118_0
# Benchmark: gsm8k
# Data Indices: [24, 187]

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
        
        # Step 1: Problem Analysis - Extract key information and classify the problem
        analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem. 
            Classify the problem type (e.g., rate, distribution, proportion). 
            Identify what the question is asking for and the expected answer format.""",
            context=""
        )
        
        # Step 2: Solution Formulation - Generate a sequence of solution steps
        solution_steps = await self.generate(
            instruction=f"""Based on the analysis: {analysis}
            Formulate a step-by-step solution plan. Include:
            - All necessary calculations
            - Intermediate results to track
            - Validation checks for each step""",
            context=analysis
        )
        
        # Step 3: Execution and Validation - Perform calculations and validate results
        steps = solution_steps.split("\n")
        intermediate_results = []
        for i, step in enumerate(steps):
            result = await self.generate(
                instruction=f"""Execute step {i+1}: {step}
                Show all calculations and intermediate results explicitly.""",
                context="\n".join(intermediate_results)
            )
            
            # Validate the result
            validation = await self.revise(
                instruction=f"""Validate the result of step {i+1}: {result}
                Check for calculation errors, logical consistency, and alignment with the problem context.""",
                context=result
            )
            
            # If validation fails, refine the result
            if "error" in validation.lower():
                refined = await self.revise(
                    instruction=f"""Refine the result of step {i+1} based on validation feedback: {validation}
                    Correct any errors and ensure accuracy.""",
                    context=result
                )
                intermediate_results.append(refined)
            else:
                intermediate_results.append(result)
        
        # Step 4: Final Output - Summarize the solution and extract the final answer
        summary = await self.summarize(
            instruction="""Condense the solution into a concise summary. 
            Highlight the final numerical answer and ensure it matches the expected format.""",
            context="\n".join(intermediate_results)
        )
        
        # Extract the final answer
        final_answer = await self.generate(
            instruction=f"""From the summary: {summary}
            Extract the final numerical answer. Ensure it is precise and formatted correctly.""",
            context=summary
        )
        
        return final_answer.strip()