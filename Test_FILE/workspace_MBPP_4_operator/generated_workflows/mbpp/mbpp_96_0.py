# Workflow ID: mbpp_96_0
# Benchmark: mbpp
# Data Indices: [169]

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
        
        # Initial analysis to extract function name and requirements
        initial_analysis = await self.generate(
            instruction="""Extract the function name, input parameters, and expected behavior from the test cases and problem description.
            Classify the problem type (e.g., mathematical, list manipulation).
            Format the output as structured information.""",
            context=""
        )
        
        # Parallel exploration of different solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Based on the analysis: {initial_analysis}
                Generate an iterative solution approach.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis: {initial_analysis}
                Generate a recursive solution approach.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Based on the analysis: {initial_analysis}
                Generate a solution using Python standard library functions.""",
                context=initial_analysis
            )
        )
        
        # Ensemble to select the best strategy
        best_strategy = await self.ensemble(
            instruction="Select the most appropriate solution based on clarity, efficiency, and adherence to best practices.",
            contexts_list=strategies
        )
        
        # Iterative refinement loop
        refined_solution = best_strategy
        for _ in range(3):  # Maximum of 3 refinement iterations
            refined_solution = await self.revise(
                instruction=f"""Refine the following solution:
                - Improve clarity and readability
                - Fix any logical errors
                - Optimize performance if possible
                
                Solution: {refined_solution}""",
                context=refined_solution
            )
            
            # Validate against test cases
            validation = await self.generate(
                instruction=f"""Validate the refined solution against the provided test cases.
                Report any discrepancies or errors.
                
                Solution: {refined_solution}""",
                context=refined_solution
            )
            
            if "error" not in validation.lower():
                break  # Exit loop if no errors are found
        
        # Final summary and synthesis
        final_summary = await self.summarize(
            instruction="Create a concise summary of the final solution, highlighting key aspects and ensuring all requirements are met.",
            context=refined_solution
        )
        
        final_code = await self.ensemble(
            instruction="Synthesize the final code from the refined solution and summary, ensuring completeness and correctness.",
            contexts_list=[refined_solution, final_summary]
        )
        
        return final_code