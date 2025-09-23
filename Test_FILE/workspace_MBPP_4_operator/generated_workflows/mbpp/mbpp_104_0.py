# Workflow ID: mbpp_104_0
# Benchmark: mbpp
# Data Indices: [147]

import asyncio  # Import inside the method as per rules
import re

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
        import re  # Required for regex-based tasks
        
        # Step 1: Extract function name and initial analysis
        initial_analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and analyze the task requirements:
            - Identify input/output types
            - Understand the operation to be performed
            - Note any constraints or special cases""",
            context=""
        )
        
        # Step 2: Parallel exploration of solution strategies
        regex_solution = await self.generate(
            instruction=f"""Generate a solution using regular expressions based on the analysis:
            {initial_analysis}
            
            Ensure proper imports and syntax.""",
            context=initial_analysis
        )
        string_manipulation_solution = await self.generate(
            instruction=f"""Generate a solution using string manipulation methods based on the analysis:
            {initial_analysis}
            
            Avoid regex and focus on built-in string functions.""",
            context=initial_analysis
        )
        
        # Step 3: Synthesize best solution
        best_solution = await self.ensemble(
            instruction="Select the most appropriate solution based on clarity, correctness, and efficiency.",
            contexts_list=[regex_solution, string_manipulation_solution]
        )
        
        # Step 4: Refine the selected solution
        refined_solution = await self.revise(
            instruction=f"""Refine the solution to ensure:
            - Proper indentation and formatting
            - All necessary imports are included
            - Logical correctness and edge case handling
            
            Original Solution:
            {best_solution}""",
            context=best_solution
        )
        
        # Step 5: Validate against test cases
        validation_result = await self.generate(
            instruction=f"""Validate the refined solution against the provided test cases:
            Refined Solution:
            {refined_solution}
            
            Check for any discrepancies or errors.""",
            context=refined_solution
        )
        
        # Step 6: Iterative improvement if needed
        if "error" in validation_result.lower():
            improved_solution = await self.revise(
                instruction=f"""Fix issues identified during validation:
                Validation Result:
                {validation_result}
                
                Original Solution:
                {refined_solution}""",
                context=refined_solution
            )
            return improved_solution
        else:
            return refined_solution