# Workflow ID: gsm8k_73_0
# Benchmark: gsm8k
# Data Indices: [171, 198]

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
            instruction="""Extract all numerical values, variables, and relationships from the problem. 
            Identify the type of problem (e.g., sequential operations, proportions, distributions). 
            Provide structured output.""",
            context=""
        )

        # Step 2: Solution Planning - Plan the sequence of operations
        solution_plan = await self.generate(
            instruction=f"""Based on the extracted information:
            {initial_analysis}
            
            Plan the sequence of operations needed to solve the problem. 
            Include all steps and their dependencies.""",
            context=initial_analysis
        )

        # Step 3: Execution and Validation - Perform calculations step-by-step
        steps = solution_plan.split("\n")
        intermediate_results = []
        for i, step in enumerate(steps):
            calculation = await self.generate(
                instruction=f"""Perform the following step:
                {step}
                
                Show all intermediate calculations and results.""",
                context="\n".join(intermediate_results)
            )
            validated_calculation = await self.revise(
                instruction=f"""Validate the following calculation:
                {calculation}
                
                Check for errors and ensure correctness.""",
                context=calculation
            )
            intermediate_results.append(validated_calculation)

        # Step 4: Final Refinement - Summarize and synthesize
        summary = await self.summarize(
            instruction="""Condense the solution path and intermediate results into a concise summary. 
            Highlight the final numerical answer.""",
            context="\n".join(intermediate_results)
        )

        final_answer = await self.ensemble(
            instruction="Extract the final numerical answer from the summary.",
            contexts_list=[summary]
        )

        # Step 5: Output the Final Answer
        return final_answer.strip()