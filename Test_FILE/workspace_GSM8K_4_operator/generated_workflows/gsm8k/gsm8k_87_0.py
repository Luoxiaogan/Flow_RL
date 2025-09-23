# Workflow ID: gsm8k_87_0
# Benchmark: gsm8k
# Data Indices: [33, 100]

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
        
        # Step 1: Initial Analysis - Extract key components and classify problem type
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure:
            - Extract all numerical values and their contexts
            - Identify relationships between numbers (e.g., rates, proportions)
            - Classify the problem type (e.g., rate, distribution, proportion)
            - Determine what the question is asking for
            Provide a structured summary.""",
            context=""
        )
        
        # Step 2: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a direct computation strategy:
                - Use the extracted information: {initial_analysis}
                - Perform calculations step-by-step
                - Show intermediate results""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop an estimation strategy:
                - Use the extracted information: {initial_analysis}
                - Approximate values using order of magnitude or rounding
                - Validate estimates against known constraints""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Develop a unit conversion strategy:
                - Use the extracted information: {initial_analysis}
                - Convert units where necessary
                - Ensure consistency in units throughout calculations""",
                context=initial_analysis
            )
        )
        
        # Step 3: Ensemble - Select the best strategy
        selected_strategy = await self.ensemble(
            instruction="""Evaluate and select the most appropriate strategy:
            - Consider accuracy, clarity, and feasibility
            - Choose the strategy that best matches the problem requirements""",
            contexts_list=strategies
        )
        
        # Step 4: Sequential Execution - Execute the selected strategy step-by-step
        intermediate_results = []
        steps = selected_strategy.split('\n')
        for step in steps:
            if step.strip():  # Skip empty lines
                result = await self.generate(
                    instruction=f"""Execute this step: {step}
                    - Perform the required calculation
                    - Track intermediate results
                    - Validate the result for logical consistency""",
                    context="\n".join(intermediate_results)
                )
                intermediate_results.append(result)
        
        # Step 5: Final Synthesis - Summarize and extract the final answer
        final_summary = await self.summarize(
            instruction="""Condense the solution into a concise format:
            - Include all key steps and intermediate results
            - Highlight the final numerical answer
            - Ensure the answer is numerically exact""",
            context="\n".join(intermediate_results)
        )
        
        # Step 6: Feedback Loop - Validate and refine if necessary
        validation = await self.generate(
            instruction=f"""Validate the solution:
            - Check for logical consistency
            - Verify arithmetic accuracy
            - Ensure units are correct
            If errors are found, suggest corrections.""",
            context=final_summary
        )
        if "error" in validation.lower():
            refined_solution = await self.revise(
                instruction=f"""Refine the solution based on validation feedback:
                - Address identified issues
                - Recalculate affected steps
                - Revalidate the refined solution""",
                context=final_summary
            )
            final_summary = refined_solution
        
        # Extract the final numerical answer
        final_answer = await self.generate(
            instruction="""Extract the final numerical answer:
            - Identify the single numerical value that answers the question
            - Ensure it is exact and properly formatted""",
            context=final_summary
        )
        
        return final_answer