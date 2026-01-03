# Workflow ID: gsm8k_82_0
# Benchmark: gsm8k
# Data Indices: [207, 211]

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

        # --- ANALYSIS PHASE ---
        analysis = await self.generate(
            instruction="""Extract all key information from the problem:
            - Identify numerical values and their units
            - Determine relationships between entities
            - Classify the problem type (e.g., rate, proportion, distribution)
            - Highlight any constraints or conditions
            Provide a structured summary.""",
            context=""
        )

        # --- PLANNING PHASE ---
        plan = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Create a step-by-step solution plan:
            - List the sequence of operations
            - Specify intermediate results to track
            - Note any special considerations (e.g., unit conversions)
            Ensure the plan is clear and actionable.""",
            context=analysis
        )

        # --- EXECUTION PHASE ---
        steps = plan.split("\n")  # Assume plan is formatted as a list of steps
        intermediate_results = []
        cumulative_context = analysis

        for i, step in enumerate(steps):
            step_result = await self.generate(
                instruction=f"""Execute step {i+1} of the solution plan:
                Step: {step}
                
                Perform the calculation and provide the result.
                Include intermediate results and units.""",
                context=cumulative_context
            )
            intermediate_results.append(step_result)
            cumulative_context += f"\nStep {i+1} Result: {step_result}"

        # Combine intermediate results into a final context
        final_context = "\n".join(intermediate_results)

        # --- VALIDATION PHASE ---
        validation = await self.generate(
            instruction=f"""Validate the solution:
            Intermediate Results:
            {final_context}
            
            Check for:
            - Consistency between steps
            - Correctness of calculations
            - Final answer matches the problem requirements
            Provide feedback on any issues.""",
            context=final_context
        )

        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Refine the solution based on validation feedback:
                Feedback: {validation}
                
                Correct any mistakes and re-calculate if necessary.""",
                context=final_context
            )
            final_answer = refined_solution
        else:
            final_answer = final_context.split("Final Answer:")[-1].strip()

        return final_answer